"""Check what people said in meeting notes against what was measured.

A note saying "streaming is up massively" is a claim. If the usage data for the
same product shows a clear fall over the same season, the rep must know before
repeating the claim to the client. This tool states agreement or conflict as a
fact that cites both the note and the usage rows.

Deliberately narrow: it only compares a direction (up or down) for a product the
sentence names, against the year-on-year figure from the usage tool. It does not
try to understand the sentence beyond that.
"""

from __future__ import annotations

import re

from client_intel.db import Dataset
from client_intel.evidence import OK, FactBuilder, ToolResult, fmt_pct
from client_intel.tools.notes import get_meeting_notes
from client_intel.tools.usage import get_usage_trend

UP_WORDS = ("up ", "up.", "growing", "growth", "grew", "increas", "record", "success", "rising")
DOWN_WORDS = ("down ", "down.", "drop", "declin", "fell", "falling", "less ", "reduc", "shrink")
# A change smaller than this either way neither supports nor contradicts a claim.
CLEAR_CHANGE_PCT = 10.0
# Words too general to identify one product ("live" is in three product names).
_STOP = {"live", "match", "feed", "data", "monitoring", "analytics", "engagement"}


def product_keywords(ds: Dataset) -> dict[str, str]:
    """Word stem -> product id, for stems that belong to exactly one product."""
    owners: dict[str, set[str]] = {}
    for pid, product in ds.products.items():
        for word in re.findall(r"[a-z]+", product["product_name"].lower()):
            if len(word) >= 5 and word not in _STOP:
                owners.setdefault(word[:6], set()).add(pid)
    return {stem: next(iter(pids)) for stem, pids in owners.items() if len(pids) == 1}


def _direction(sentence: str) -> str | None:
    text = f"{sentence.lower()} "
    up = any(w in text for w in UP_WORDS)
    down = any(w in text for w in DOWN_WORDS)
    if up == down:
        return None  # no direction, or both: not a clear claim
    return "up" if up else "down"


def check_claims(ds: Dataset, client_id: str) -> ToolResult:
    fb = FactBuilder("claim_check")
    notes = get_meeting_notes(ds, client_id).data.get("notes", [])
    usage = get_usage_trend(ds, client_id).data.get("products", {})
    keywords = product_keywords(ds)
    checked: list[dict[str, object]] = []

    for note in notes:
        for quote in note["quotes"]:
            sentence: str = quote["text"]
            direction = _direction(sentence)
            lowered = sentence.lower()
            products = sorted({pid for stem, pid in keywords.items() if stem in lowered})
            if direction is None or not products:
                continue
            for pid in products:
                measured = usage.get(pid)
                cite_note = f"note:{note['note_id']}"
                if measured is None:
                    # They talk about a product they have no usage for: interest, not a
                    # measurable claim. The white-space tool covers that angle.
                    continue
                yoy = measured.get("yoy_pct")
                if yoy is None:
                    fb.gap(
                        "claim_not_checkable",
                        f"Note {note['note_id']} makes a claim about {pid} that cannot be "
                        "checked: no year-on-year usage figure is available.",
                        [cite_note],
                    )
                    continue
                months = set(measured["recent_months"]) | set(measured["year_ago_months"])
                rows = [
                    f"usage:{m['usage_id']}" for m in measured["series"] if m["month"] in months
                ]
                if abs(yoy) < CLEAR_CHANGE_PCT:
                    verdict = "not_clear"
                elif (yoy > 0) == (direction == "up"):
                    verdict = "consistent"
                else:
                    verdict = "conflict"
                checked.append({"note_id": note["note_id"], "product_id": pid,
                                "claimed": direction, "yoy_pct": yoy, "verdict": verdict})
                # Sentences with digits are not quoted: a figure someone said must not
                # enter a fact that reads as measured.
                said = f': "{sentence}"' if not re.search(r"\d", sentence) else ""
                base = (f"Note {note['note_id']} of {note['meeting_date']} reports {pid} usage "
                        f"as going {direction}{said}")
                measured_text = (f"measured {pid} usage changed {fmt_pct(yoy)} year on year "
                                 "over the last three complete months")
                if verdict == "conflict":
                    fb.calc(f"{base} This conflicts with the data: {measured_text}.",
                            [cite_note, *rows], topic="source_conflict", signal="risk")
                    fb.gap("source_conflict",
                           f"Note {note['note_id']} and the usage data disagree about {pid}; "
                           "the briefing uses the measured figure.", [cite_note])
                elif verdict == "consistent":
                    fb.calc(f"{base} The data agrees: {measured_text}.",
                            [cite_note, *rows], topic="claim_confirmed", signal="neutral")
                else:
                    fb.calc(f"{base} The data shows no clear change: {measured_text}.",
                            [cite_note, *rows], topic="claim_unclear", signal="neutral")

    # Nothing to compare is a normal outcome here, not missing data.
    return fb.result(OK, {"client_id": client_id, "checked": checked})

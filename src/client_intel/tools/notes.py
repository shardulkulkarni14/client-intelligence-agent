"""Meeting notes: what people wrote after meetings, quoted, never measured.

Everything from a note is kind "reported". A figure inside a note ("+10%", "up
massively") is a person's claim; the usage and contract tools hold the measurements.
Extraction is a plain keyword filter so the same note always yields the same quotes.
"""

from __future__ import annotations

import re
from typing import Any

from client_intel.db import Dataset
from client_intel.evidence import (
    NO_DATA,
    OK,
    FactBuilder,
    ToolResult,
    cite,
    fmt_date,
    fmt_num,
)

TOOL = "meeting_notes"

MAX_QUOTES_PER_NOTE = 6

# Checked in this order; the first matching group names the fact's topic. Each entry is
# matched at the start of a word, case-insensitively ("complain" matches "Complaints").
KEYWORDS: dict[str, tuple[str, ...]] = {
    "commitment": ("actions:", "action:", "agreed to", "promised", "committed"),
    "competitor": ("competitor", "supplier", "trial", "alternative", "instead of", "switch"),
    "complaint": (
        "complain",
        "delay",
        "worried",
        "concern",
        "cooler",
        "suspend",
        "could not",
        "unhappy",
        "frustrat",
        "service credit",
        "explanation",
        "pressure",
    ),
    "pricing": ("price", "pricing", "budget", "cost", "overage", "bill", "discount", "credit"),
    "renewal": ("renewal", "renew", "notice", "legal", "contract", "terms"),
    "growth": (
        "growth",
        "growing",
        "up massively",
        "record",
        "expand",
        "launch",
        "interest",
        "keen",
        "want to add",
        "add the",
        "asked whether",
        "asked about",
        "larger",
        "success",
    ),
}
RISK_TOPICS = ("competitor", "complaint")

# Header lines of the note file that repeat the index and are not statements.
_HEADER_RE = re.compile(r"^(#|date:|author:|attendees:)", re.I)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")
_NO_ACTION_RE = re.compile(r"^actions?:\s*none\.?$", re.I)
_PATTERNS: dict[str, re.Pattern[str]] = {
    topic: re.compile(r"(?<![A-Za-z])(?:" + "|".join(re.escape(w) for w in words) + ")", re.I)
    for topic, words in KEYWORDS.items()
}


def split_statements(body: str) -> list[str]:
    """Sentences and bullets of a note body, verbatim, without the header lines."""
    statements: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or _HEADER_RE.match(line):
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        statements.extend(s.strip() for s in _SENTENCE_RE.split(line) if s.strip())
    return statements


def classify(statement: str) -> str | None:
    """The first keyword group the statement matches, or None if it is not kept."""
    if _NO_ACTION_RE.match(statement):
        return None
    for topic, pattern in _PATTERNS.items():
        if pattern.search(statement):
            return topic
    return None


def get_meeting_notes(ds: Dataset, client_id: str) -> ToolResult:
    fb = FactBuilder(TOOL)
    if client_id not in ds.clients:
        fb.gap("unknown_client", f"No client with ID {client_id} in the data.")
        return fb.result(NO_DATA)

    notes = sorted(
        ds.for_client("notes", client_id),
        key=lambda n: (n["meeting_date"], n["note_id"]),
        reverse=True,
    )
    if not notes:
        fb.gap(
            "no_meeting_notes",
            "No meeting notes exist for this client, so there is no relationship context "
            "from notes.",
        )
        return fb.result(NO_DATA, data={"client_id": client_id, "note_count": 0, "notes": []})

    latest = notes[0]
    days_since = (ds.as_of - latest["meeting_date"]).days
    fb.calc(
        f"{fmt_num(len(notes))} meeting {'note' if len(notes) == 1 else 'notes'} on record; "
        f"the last meeting was {fmt_date(latest['meeting_date'])}, {fmt_num(days_since)} days "
        f"before {fmt_date(ds.as_of)}.",
        rows=[cite("note", n["note_id"]) for n in notes],
        topic="last_meeting",
        signal="neutral",
    )

    notes_data: list[dict[str, Any]] = []
    for note in notes:
        note_cite = cite("note", note["note_id"])
        body = note.get("body") or ""
        fb.reported(
            note_cite,
            f"Note {note['note_id']}: \"{note.get('title') or 'untitled'}\" on "
            f"{fmt_date(note['meeting_date'])}, written by {note.get('author') or 'unknown'}.",
            topic="note",
            signal="neutral",
        )
        quotes: list[dict[str, str]] = []
        if not body.strip():
            fb.gap("empty_note", f"Note {note['note_id']} has no text.", [note_cite])
        for statement in split_statements(body):
            if len(quotes) >= MAX_QUOTES_PER_NOTE:
                break
            topic = classify(statement)
            if topic is None:
                continue
            quotes.append({"topic": topic, "text": statement})
            fb.reported(
                note_cite,
                f"Note {note['note_id']} ({fmt_date(note['meeting_date'])}) says: "
                f"\"{statement}\"",
                topic=topic,
                signal="risk" if topic in RISK_TOPICS else "neutral",
            )
        notes_data.append(
            {
                "note_id": note["note_id"],
                "meeting_date": note["meeting_date"],
                "author": note.get("author"),
                "title": note.get("title"),
                "body": body,
                "quotes": quotes,
            }
        )

    return fb.result(
        OK,
        data={
            "client_id": client_id,
            "note_count": len(notes),
            "last_meeting_date": latest["meeting_date"],
            "days_since_last_meeting": days_since,
            "notes": notes_data,
        },
    )

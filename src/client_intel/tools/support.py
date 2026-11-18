"""Support summary: ticket volume, severity, open tickets and satisfaction for one client.

Windows are counted back from the extract date by opened_date. Ticket subjects are
quoted as reported; many generic subjects in this data do not match their category,
so the tool never interprets them.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from client_intel.db import Dataset, Row
from client_intel.evidence import (
    NO_DATA,
    OK,
    FactBuilder,
    ToolResult,
    cite,
    fmt_date,
    fmt_num,
    fmt_pct,
    pct_change,
)

TOOL = "support_summary"

WINDOWS: tuple[tuple[str, int, str], ...] = (
    ("12m", 365, "last 12 months"),
    ("90d", 90, "last 90 days"),
)
TREND_DAYS = 90  # last 90 days versus the 90 days before
MIN_BASE_FOR_PCT = 5  # no percentage change on a base smaller than this
RISING_MIN_DELTA = 2  # one extra ticket is noise, not a rising count
CSAT_RISK_BELOW = 3.5
CSAT_MIN_RATINGS = 3
TOP_CATEGORIES = 3
MAX_ROWS = 40  # cap on row IDs carried by a calc fact; the full list is in data
HIGH_PRIORITIES = ("P1", "P2")
OPEN_STATUS = "open"  # the data has exactly two statuses: open and closed


def _in_window(tickets: list[Row], start: date, end: date) -> list[Row]:
    """Tickets opened after `start` and up to and including `end`."""
    return [t for t in tickets if t["opened_date"] is not None and start < t["opened_date"] <= end]


def _rows(tickets: list[Row]) -> list[str]:
    return [cite("ticket", t["ticket_id"]) for t in tickets[:MAX_ROWS]]


def _plural(n: int, word: str = "ticket") -> str:
    return f"{fmt_num(n)} {word}" if n == 1 else f"{fmt_num(n)} {word}s"


def _window_stats(tickets: list[Row]) -> dict[str, Any]:
    rated = [t for t in tickets if t.get("csat_score") is not None]
    closed = [t for t in tickets if t.get("closed_date") is not None]
    by_priority = Counter(t.get("priority") or "unknown" for t in tickets)
    by_category = Counter(t.get("category") or "unknown" for t in tickets)
    return {
        "count": len(tickets),
        "ticket_ids": [t["ticket_id"] for t in tickets],
        "by_priority": dict(sorted(by_priority.items())),
        "by_category": dict(sorted(by_category.items(), key=lambda kv: (-kv[1], kv[0]))),
        "p1_p2_count": sum(1 for t in tickets if t.get("priority") in HIGH_PRIORITIES),
        "csat_avg": (sum(t["csat_score"] for t in rated) / len(rated)) if rated else None,
        "csat_rated": len(rated),
        "closed_count": len(closed),
        "avg_resolution_days": (
            sum((t["closed_date"] - t["opened_date"]).days for t in closed) / len(closed)
            if closed
            else None
        ),
    }


def get_support_summary(ds: Dataset, client_id: str) -> ToolResult:
    fb = FactBuilder(TOOL)
    if client_id not in ds.clients:
        fb.gap("unknown_client", f"No client with ID {client_id} in the data.")
        return fb.result(NO_DATA)

    as_of = ds.as_of
    tickets = sorted(
        ds.for_client("tickets", client_id), key=lambda t: (t["opened_date"], t["ticket_id"])
    )
    if not tickets:
        fb.gap(
            "no_support_tickets",
            "No support tickets are recorded for this client. That means no ticket data, "
            "not that the client has no problems.",
        )
        return fb.result(NO_DATA, data={"client_id": client_id, "total_tickets": 0})

    latest = tickets[-1]
    fb.calc(
        f"{_plural(len(tickets))} on record in total; the most recent was opened "
        f"{fmt_date(latest['opened_date'])}.",
        rows=_rows(tickets),
        topic="support_overview",
        signal="neutral",
    )

    data: dict[str, Any] = {
        "client_id": client_id,
        "as_of": as_of,
        "total_tickets": len(tickets),
        "all_ticket_ids": [t["ticket_id"] for t in tickets],
        "windows": {},
    }

    for key, days, label in WINDOWS:
        start = as_of - timedelta(days=days)
        window = _in_window(tickets, start, as_of)
        stats = _window_stats(window)
        stats["start_exclusive"] = start
        stats["end_inclusive"] = as_of
        data["windows"][key] = stats
        topic = f"support_{key}"
        rows = _rows(window)

        if not window:
            fb.calc(
                f"No tickets were opened in the {label} (after {fmt_date(start)}).",
                rows=[],
                topic=topic,
                signal="neutral",
            )
            continue

        priority_text = ", ".join(
            f"{p}: {fmt_num(n)}" for p, n in stats["by_priority"].items()
        )
        fb.calc(
            f"{_plural(stats['count'])} opened in the {label}; by priority {priority_text}.",
            rows=rows,
            topic=topic,
            signal="neutral",
        )
        top = list(stats["by_category"].items())[:TOP_CATEGORIES]
        fb.calc(
            f"Top ticket categories in the {label}: "
            + ", ".join(f"{c} ({fmt_num(n)})" for c, n in top)
            + ".",
            rows=rows,
            topic=topic,
            signal="neutral",
        )
        high = [t for t in window if t.get("priority") in HIGH_PRIORITIES]
        fb.calc(
            f"{_plural(len(high), 'P1/P2 ticket')} opened in the {label}.",
            rows=_rows(high),
            topic=topic,
            signal="neutral",
        )
        rated = [t for t in window if t.get("csat_score") is not None]
        if rated:
            low = stats["csat_avg"] < CSAT_RISK_BELOW and len(rated) >= CSAT_MIN_RATINGS
            fb.calc(
                f"Average CSAT in the {label} is {fmt_num(stats['csat_avg'], 1)} out of "
                f"{fmt_num(5)}, from {_plural(len(rated), 'rated ticket')}.",
                rows=_rows(rated),
                topic=f"csat_{key}",
                signal="risk" if low else "neutral",
            )
        else:
            fb.calc(
                f"Average CSAT in the {label}: n/a, no rated tickets.",
                rows=[],
                topic=f"csat_{key}",
                signal="neutral",
            )
        closed = [t for t in window if t.get("closed_date") is not None]
        if closed:
            fb.calc(
                f"Closed tickets opened in the {label} took "
                f"{fmt_num(stats['avg_resolution_days'], 1)} days on average to resolve "
                f"({_plural(len(closed), 'closed ticket')}).",
                rows=_rows(closed),
                topic=topic,
                signal="neutral",
            )
        else:
            fb.calc(
                f"Average resolution time in the {label}: n/a, no closed tickets.",
                rows=[],
                topic=topic,
                signal="neutral",
            )

    # Volume change: counts only, a percentage only on a base that can carry one.
    recent_start = as_of - timedelta(days=TREND_DAYS)
    previous_start = as_of - timedelta(days=2 * TREND_DAYS)
    recent = _in_window(tickets, recent_start, as_of)
    previous = _in_window(tickets, previous_start, recent_start)
    delta = len(recent) - len(previous)
    rising = delta >= RISING_MIN_DELTA
    direction = "up" if delta > 0 else "down" if delta < 0 else "unchanged"
    text = (
        f"Ticket volume is {direction}: {fmt_num(len(recent))} opened in the last "
        f"{fmt_num(TREND_DAYS)} days versus {fmt_num(len(previous))} in the previous "
        f"{fmt_num(TREND_DAYS)} days"
    )
    change = pct_change(len(recent), len(previous))
    if len(previous) >= MIN_BASE_FOR_PCT and change is not None:
        text += f" ({fmt_pct(change)})"
    fb.calc(
        text + ".",
        rows=_rows(previous + recent),
        topic="ticket_trend",
        signal="risk" if rising else "neutral",
    )
    data["trend"] = {
        "recent_count": len(recent),
        "previous_count": len(previous),
        "recent_ids": [t["ticket_id"] for t in recent],
        "previous_ids": [t["ticket_id"] for t in previous],
        "delta": delta,
        "rising": rising,
        "pct_change": change if len(previous) >= MIN_BASE_FOR_PCT else None,
    }

    # Open tickets now, whatever their age.
    open_tickets = [t for t in tickets if t.get("status") == OPEN_STATUS]
    open_high = [t for t in open_tickets if t.get("priority") in HIGH_PRIORITIES]
    if open_tickets:
        fb.calc(
            f"{_plural(len(open_tickets), 'open ticket')} at {fmt_date(as_of)}, of which "
            f"{fmt_num(len(open_high))} are P1/P2.",
            rows=_rows(open_tickets),
            topic="open_tickets",
            signal="risk" if open_high else "neutral",
        )
    else:
        fb.calc(
            f"No open tickets at {fmt_date(as_of)}.",
            rows=[],
            topic="open_tickets",
            signal="neutral",
        )
    open_data: list[dict[str, Any]] = []
    for t in open_tickets:
        age = (as_of - t["opened_date"]).days
        open_data.append(
            {
                "ticket_id": t["ticket_id"],
                "priority": t.get("priority"),
                "category": t.get("category"),
                "product_id": t.get("product_id"),
                "opened_date": t["opened_date"],
                "age_days": age,
                "subject": t.get("subject"),
            }
        )
        fb.reported(
            cite("ticket", t["ticket_id"]),
            f"Open ticket {t['ticket_id']}: priority {t.get('priority') or 'unknown'}, "
            f"category {t.get('category') or 'unknown'}, product "
            f"{t.get('product_id') or 'unknown'}, opened {fmt_date(t['opened_date'])}, open for "
            f"{fmt_num(age)} days; subject as reported: \"{t.get('subject') or ''}\".",
            topic="open_tickets",
            signal="risk" if t.get("priority") in HIGH_PRIORITIES else "neutral",
        )
    data["open_tickets"] = open_data
    data["open_count"] = len(open_tickets)
    data["open_p1_p2_count"] = len(open_high)

    return fb.result(OK, data=data)

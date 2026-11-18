"""Load the starter pack into typed, de-duplicated tables.

The SQLite export stores every column as TEXT and uses '' for blanks, so nothing
downstream may compare or aggregate the raw values. This module is the only place
that reads the database: it casts each column once, turns blanks into None, removes
duplicate records in code (the source files are never edited) and records what it
removed so the briefing can say so.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

# The extract date given in the starter pack README. Usage is complete up to and
# including October 2026, so November 2026 is "not yet reported", never a gap.
AS_OF = date(2026, 11, 1)
DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "starter_pack" / "client_intel.db"

Row = dict[str, Any]

_DATE = {
    "clients": ["customer_since"],
    "contracts": ["start_date", "end_date", "signed_date"],
    "support_tickets": ["opened_date", "closed_date"],
    "crm_opportunities": ["created_date", "expected_close_date"],
    "meeting_notes": ["meeting_date"],
}
_INT = {
    "contracts": ["term_months", "notice_period_days"],
    "support_tickets": ["csat_score"],
}
_FLOAT = {
    "products": ["list_price_from_eur"],
    "contracts": ["arr_eur"],
    "contract_lines": ["annual_fee_eur", "included_units_monthly", "overage_rate_eur_per_unit"],
    "usage_monthly": ["units_used", "included_units"],
    "crm_opportunities": ["amount_eur"],
}
_LIST = {"products": ["typical_segments", "often_bought_with"]}

# Primary key per table, and the natural key where the dictionary promises uniqueness.
_PK = {
    "clients": "client_id",
    "products": "product_id",
    "contracts": "contract_id",
    "contract_lines": "line_id",
    "usage_monthly": "usage_id",
    "support_tickets": "ticket_id",
    "crm_opportunities": "opp_id",
    "meeting_notes": "note_id",
}
_NATURAL_KEY = {"usage_monthly": ("client_id", "product_id", "month")}


@dataclass(frozen=True)
class DataIssue:
    """Something wrong with the source data that was found while loading."""

    code: str  # duplicate_row | duplicate_natural_key | conflicting_natural_key
    table: str
    message: str
    rows: tuple[str, ...]
    client_id: str | None = None


@dataclass
class Dataset:
    clients: dict[str, Row]
    products: dict[str, Row]
    contracts: list[Row]
    contract_lines: list[Row]
    usage: list[Row]
    tickets: list[Row]
    opportunities: list[Row]
    notes: list[Row]
    issues: list[DataIssue] = field(default_factory=list)
    as_of: date = AS_OF

    def for_client(self, table: str, client_id: str) -> list[Row]:
        return [r for r in getattr(self, table) if r.get("client_id") == client_id]

    def contract_in_force(self, client_id: str) -> Row | None:
        """The one definition of "in force" for every tool: status active and the
        extract date inside the term (end date inclusive). A pending or expired
        contract is never in force. If several qualify, the latest start wins."""
        live = [
            c
            for c in self.for_client("contracts", client_id)
            if c["status"] == "active"
            and c["start_date"] is not None
            and c["end_date"] is not None
            and c["start_date"] <= self.as_of <= c["end_date"]
        ]
        return max(live, key=lambda c: c["start_date"]) if live else None

    def lines_for(self, contract_id: str) -> list[Row]:
        return [r for r in self.contract_lines if r["contract_id"] == contract_id]


def _cast(table: str, row: Row) -> Row:
    out: Row = {}
    for key, raw in row.items():
        value = raw.strip() if isinstance(raw, str) else raw
        if value == "" or value is None:
            out[key] = [] if key in _LIST.get(table, []) else None
        elif key in _DATE.get(table, []):
            out[key] = date.fromisoformat(value)
        elif key in _INT.get(table, []):
            out[key] = int(float(value))
        elif key in _FLOAT.get(table, []):
            out[key] = float(value)
        elif key in _LIST.get(table, []):
            out[key] = [part.strip() for part in value.split(";") if part.strip()]
        else:
            out[key] = value
    return out


def _dedupe(table: str, rows: list[Row], issues: list[DataIssue]) -> list[Row]:
    """Drop repeated records, keeping the first, and record each removal."""
    pk = _PK[table]
    kept: list[Row] = []
    seen_rows: dict[tuple, Row] = {}
    for row in rows:
        fingerprint = tuple(sorted((k, str(v)) for k, v in row.items()))
        if fingerprint in seen_rows:
            issues.append(
                DataIssue(
                    code="duplicate_row",
                    table=table,
                    message=f"{table} row {row[pk]} appears twice with identical values; "
                    "counted once.",
                    rows=(row[pk],),
                    client_id=row.get("client_id"),
                )
            )
            continue
        seen_rows[fingerprint] = row
        kept.append(row)

    natural = _NATURAL_KEY.get(table)
    if not natural:
        return kept
    result: list[Row] = []
    by_key: dict[tuple, Row] = {}
    for row in kept:
        key = tuple(row[k] for k in natural)
        first = by_key.get(key)
        if first is None:
            by_key[key] = row
            result.append(row)
            continue
        same = all(first[k] == row[k] for k in row if k != pk)
        label = "/".join(str(k) for k in key)
        if same:
            issues.append(
                DataIssue(
                    code="duplicate_natural_key",
                    table=table,
                    message=f"{table} rows {first[pk]} and {row[pk]} are the same record "
                    f"({label}) under two IDs; counted once.",
                    rows=(first[pk], row[pk]),
                    client_id=row.get("client_id"),
                )
            )
        else:
            # Two different values for one month: neither is trustworthy, so keep the
            # first for continuity and say plainly that the month is disputed.
            issues.append(
                DataIssue(
                    code="conflicting_natural_key",
                    table=table,
                    message=f"{table} rows {first[pk]} and {row[pk]} give different values "
                    f"for {label}; the first is used and the figure is unreliable.",
                    rows=(first[pk], row[pk]),
                    client_id=row.get("client_id"),
                )
            )
    return result


def load(db_path: Path | str = DEFAULT_DB, as_of: date = AS_OF) -> Dataset:
    """Read every table once, read-only, and return typed, de-duplicated data."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    issues: list[DataIssue] = []
    tables: dict[str, list[Row]] = {}
    try:
        for table in _PK:
            raw = [dict(r) for r in conn.execute(f"SELECT * FROM {table}")]  # noqa: S608
            tables[table] = _dedupe(table, [_cast(table, r) for r in raw], issues)
    finally:
        conn.close()
    return Dataset(
        clients={r["client_id"]: r for r in tables["clients"]},
        products={r["product_id"]: r for r in tables["products"]},
        contracts=tables["contracts"],
        contract_lines=tables["contract_lines"],
        usage=tables["usage_monthly"],
        tickets=tables["support_tickets"],
        opportunities=tables["crm_opportunities"],
        notes=tables["meeting_notes"],
        issues=issues,
        as_of=as_of,
    )

"""The shared format every tool returns and the writer and verifier consume.

A tool never returns prose for the model to interpret. It returns facts: one
sentence each, with every figure already formatted by code and with the citation
IDs of the rows it came from. The writer may only repeat these figures; the verifier
checks each number in the briefing against the facts cited on the same line.

Citation IDs follow the starter pack's tool catalogue:
  contracts:K-0002   usage:U-00422   ticket:T-0123   opp:O-0001   note:N-003
  product:WIDGETS    client:C001     calc:<tool>#<n>  (a value computed by a tool)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

# kind of a fact
DATA = "data"  # read directly from one or more rows
CALC = "calc"  # computed by a tool from the listed rows
REPORTED = "reported"  # quoted from free text (notes, ticket subjects, CRM next steps)

OK = "ok"
NO_DATA = "no_data"  # the tool ran and there is nothing for this client
PARTIAL = "partial"  # the tool ran but part of the answer could not be computed


@dataclass
class Fact:
    id: str  # the citation the writer must use for this fact, e.g. "calc:usage_trend#3"
    text: str  # one sentence, figures formatted with the helpers below
    rows: list[str] = field(default_factory=list)  # source row citations, e.g. "usage:U-00422"
    kind: str = DATA
    topic: str = ""  # short grouping key, e.g. "renewal", "utilisation", "open_tickets"
    signal: str = ""  # optional reading for the planner: "risk" | "opportunity" | "neutral" | ""


@dataclass
class Gap:
    """Missing, sparse or inconsistent data the briefing must admit."""

    code: str  # e.g. missing_month, short_history, no_contract_in_force, source_conflict
    text: str
    rows: list[str] = field(default_factory=list)


@dataclass
class ToolResult:
    tool: str
    status: str = OK
    facts: list[Fact] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)  # raw numbers for the evidence file

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


class FactBuilder:
    """Issues stable calc IDs for one tool run: calc:<tool>#1, #2, ..."""

    def __init__(self, tool: str) -> None:
        self.tool = tool
        self._n = 0
        self.facts: list[Fact] = []
        self.gaps: list[Gap] = []

    def data(self, cite: str, text: str, topic: str = "", signal: str = "") -> Fact:
        """A fact read straight from one row; the row citation is the fact's ID."""
        fact = Fact(id=cite, text=text, rows=[cite], kind=DATA, topic=topic, signal=signal)
        self.facts.append(fact)
        return fact

    def calc(self, text: str, rows: list[str], topic: str = "", signal: str = "") -> Fact:
        """A value computed by the tool; gets its own calc ID and lists its inputs."""
        self._n += 1
        fact = Fact(
            id=f"calc:{self.tool}#{self._n}",
            text=text,
            rows=list(rows),
            kind=CALC,
            topic=topic,
            signal=signal,
        )
        self.facts.append(fact)
        return fact

    def reported(self, cite: str, text: str, topic: str = "", signal: str = "") -> Fact:
        """Something a person wrote (note, ticket subject, CRM next step). Not measured."""
        fact = Fact(id=cite, text=text, rows=[cite], kind=REPORTED, topic=topic, signal=signal)
        self.facts.append(fact)
        return fact

    def gap(self, code: str, text: str, rows: list[str] | None = None) -> Gap:
        gap = Gap(code=code, text=text, rows=list(rows or []))
        self.gaps.append(gap)
        return gap

    def result(self, status: str = OK, data: dict[str, Any] | None = None) -> ToolResult:
        return ToolResult(
            tool=self.tool, status=status, facts=self.facts, gaps=self.gaps, data=data or {}
        )


# --- formatting: the only place figures are turned into text -----------------


def fmt_eur(value: float | None) -> str:
    """752000 -> 'EUR 752,000'. Whole euros; the data has no cents that matter."""
    return "n/a" if value is None else f"EUR {round(value):,}"


def fmt_num(value: float | None, decimals: int = 0) -> str:
    """8631 -> '8,631'; 12.5 with decimals=1 -> '12.5'."""
    if value is None:
        return "n/a"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float | None, signed: bool = True) -> str:
    """-28.04 -> '-28.0%'. Input is already in percent, one decimal, sign shown."""
    if value is None:
        return "n/a"
    return f"{value:+.1f}%" if signed else f"{value:.1f}%"


def fmt_date(value: date | None) -> str:
    return "n/a" if value is None else value.isoformat()


def pct_change(new: float | None, old: float | None) -> float | None:
    """Percent change, or None when it cannot be computed (no base or zero base)."""
    if new is None or old is None or old == 0:
        return None
    return (new - old) / old * 100.0


def cite(prefix: str, row_id: str) -> str:
    return f"{prefix}:{row_id}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if isinstance(value, date):
        return value.isoformat()
    return value

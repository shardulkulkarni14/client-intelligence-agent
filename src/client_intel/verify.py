"""Checks a written briefing against the evidence, in code, with no model involved.

The writer is a language model, so nothing it writes is trusted. Each line of the
briefing is checked on its own: every number on the line must appear in the text of
a fact cited on that same line. A line never inherits citations from its neighbours.

Normalisation (how a written number is compared with an evidence number):
  * thousands separators are dropped: "8,631" == "8631";
  * signs are ignored: "down 28.0%" matches "-28.0%" (direction is NOT checked);
  * the evidence value is rounded half-up to the precision the writer used and must
    then be equal: "28%" matches "-28.0%", "45%" does not match "45.5%" (that is 46);
  * "EUR 752,000", "€752,000" and "752,000 EUR" are money and match only money;
    "28.0%" / "28.0 percent" are percentages and match only percentages; a bare
    number ("752,000") matches a plain, money or percentage figure of that value;
  * abbreviations ("752k", "0.75m", "2 million") never match, so the writer has to
    copy figures exactly as the tools formatted them;
  * ISO dates ("2026-12-31") are one token and must match exactly; "YYYY-MM" matches
    the same month or an ISO date inside that month;
  * a bare year ("Oct 2026", "FY2026") is a number; it is supported by that number
    or by a date/month of that year in the evidence or the allowed text.

Not treated as numbers: citation brackets, row and client IDs (K-0002, C001,
U-00422, T-0123, O-0001, N-003), priorities and quarter labels (P1, Q3), product
ids (ODDS_LIVE), ordered-list markers, heading lines.

Known limits:
  * number words ("three open tickets", one..twelve) are NOT checked;
  * only numbers are checked, not names, adjectives or the direction of a change;
  * day and month-name dates ("31 December 2026") are not date tokens: the year is
    checked as a year and the day as a plain number, so the writer should use ISO;
  * a wrapped paragraph is checked per physical line, so the citation must sit on
    the same line as the number;
  * a citation of a source row brings in every fact computed from that row.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from client_intel.evidence import REPORTED, Fact

UNKNOWN_CITATION = "unknown_citation"
NOT_IN_CITED = "number_not_in_cited_evidence"
NO_CITATION = "number_without_citation"
ONLY_REPORTED = "number_only_reported"

EUR = "eur"
PERCENT = "percent"
NUMBER = "number"
DATE = "date"
MONTH = "month"
ABBREVIATED = "abbreviated"


@dataclass(frozen=True)
class NumberToken:
    raw: str  # as written, e.g. "EUR 752,000"
    value: str  # normalised: "752000", "28.0", "2026-12-31"
    kind: str  # eur | percent | number | date | month | abbreviated


@dataclass
class Violation:
    line_no: int  # 1-based line in the briefing
    line: str
    kind: str
    token: str  # the offending number or citation as written
    detail: str


@dataclass
class VerificationReport:
    ok: bool
    numbers_checked: int
    citations_checked: int
    violations: list[Violation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- citations ---------------------------------------------------------------

_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
_CITATION_ID_RE = re.compile(r"[a-z_]+:[A-Za-z0-9_.\-]+(?:#\d+)?")
_FLAG_RE = re.compile(r"\[UNVERIFIED:[^\[\]]*\]")


def _bracket_citations(content: str) -> list[str]:
    """IDs in one bracket, or [] when the bracket is not a citation (a link, a flag)."""
    parts = [p.strip() for p in re.split(r"[;,]", content)]
    if not parts or not all(_CITATION_ID_RE.fullmatch(p) for p in parts):
        return []
    return parts


def extract_citations(line: str) -> list[str]:
    """Citations in order of appearance; '[a][b]', '[a; b]' and '[a, b]' all work."""
    found: list[str] = []
    for match in _BRACKET_RE.finditer(line):
        found.extend(_bracket_citations(match.group(1)))
    return found


def _blank_citations(line: str) -> str:
    """Replace citation brackets by spaces so 'calc:usage_trend#3' is not read as 3."""

    def blank(match: re.Match[str]) -> str:
        return " " * len(match.group(0)) if _bracket_citations(match.group(1)) else match.group(0)

    # Our own flag repeats the offending figure; re-verifying a flagged briefing
    # must not count it a second time.
    return _BRACKET_RE.sub(blank, _FLAG_RE.sub(lambda m: " " * len(m.group(0)), line))


# --- numbers -----------------------------------------------------------------

_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_ABBREV = r"(?:(?:[kKmM]|bn|mn)\b|\s?(?i:mio|thousand|million|billion)\b)"

_TOKEN_RE = re.compile(
    rf"""
    (?P<date>(?<![\w-])\d{{4}}-\d{{2}}-\d{{2}}(?![\w-]))
    | (?P<month>(?<![\w-])\d{{4}}-(?:0[1-9]|1[0-2])(?![\w-]))
    | (?P<barecite>\b[a-z_]+:[A-Za-z][\w-]*(?:\#\d+)?)       # a citation without brackets
    | (?P<id>\b(?:[A-Z]-\d+|[A-Z]\d+|[A-Z][A-Z0-9]*_[A-Z0-9_]+)\b)
    | (?P<eur_pre>(?<![A-Za-z])(?:EUR|€)\s?[-+−]?(?P<n1>{_NUM})(?P<a1>{_ABBREV})?)
    | (?P<num>(?<!\d)(?<!\d[.,])(?P<n2>{_NUM})(?P<a2>{_ABBREV})?
        (?P<pct>\s?%|\s(?:percent|per\scent)\b)?
        (?P<eur_post>\s?(?:EUR\b|€|euros?\b))?)
    """,
    re.VERBOSE,
)

_LIST_MARKER_RE = re.compile(r"^(\s*(?:[-*+>]\s+)*)(\d+[.)])(?=\s)")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}(?:\s|$)")


def _blank_list_marker(line: str) -> str:
    return _LIST_MARKER_RE.sub(lambda m: m.group(1) + " " * len(m.group(2)), line)


def extract_numbers(text: str) -> list[NumberToken]:
    """Every checkable figure in the text: raw form, normalised value and type."""
    tokens: list[NumberToken] = []
    for raw_line in text.splitlines():
        line = _blank_list_marker(_blank_citations(raw_line))
        for m in _TOKEN_RE.finditer(line):
            if m.group("date"):
                tokens.append(NumberToken(m.group("date"), m.group("date"), DATE))
            elif m.group("month"):
                tokens.append(NumberToken(m.group("month"), m.group("month"), MONTH))
            elif m.group("eur_pre"):
                kind = ABBREVIATED if m.group("a1") else EUR
                value = m.group("n1").replace(",", "")
                tokens.append(NumberToken(m.group("eur_pre"), value, kind))
            elif m.group("num"):
                if m.group("a2"):
                    kind = ABBREVIATED
                elif m.group("pct"):
                    kind = PERCENT
                elif m.group("eur_post"):
                    kind = EUR
                else:
                    kind = NUMBER
                value = m.group("n2").replace(",", "")
                tokens.append(NumberToken(m.group("num"), value, kind))
    return tokens


def _same_value(written: str, evidence: str) -> bool:
    """Evidence rounded half-up to the written precision equals the written number."""
    decimals = len(written.split(".")[1]) if "." in written else 0
    quantum = Decimal(1).scaleb(-decimals)
    rounded = Decimal(evidence).quantize(quantum, rounding=ROUND_HALF_UP)
    return rounded == Decimal(written)


def _is_year(token: NumberToken) -> bool:
    return (
        token.kind == NUMBER
        and len(token.raw) == 4
        and token.raw.isdigit()
        and 1900 <= int(token.raw) <= 2100
    )


def _supports(written: NumberToken, evidence: NumberToken) -> bool:
    if ABBREVIATED in (written.kind, evidence.kind):
        return False
    if written.kind == DATE:
        return evidence.kind == DATE and evidence.value == written.value
    if written.kind == MONTH:
        return evidence.kind in (DATE, MONTH) and evidence.value[:7] == written.value
    if evidence.kind in (DATE, MONTH):
        return _is_year(written) and evidence.value[:4] == written.value
    if written.kind in (EUR, PERCENT) and evidence.kind != written.kind:
        return False
    return _same_value(written.value, evidence.value)


# --- verification ------------------------------------------------------------

_MARKER_RE = re.compile(
    r"\b(?:reported(?:ly)?|according\s+to|said|says|stated|claimed|quoted|noted|mentioned)\b"
    r"|[\"“”„«»]",
    re.IGNORECASE,
)


class _Evidence:
    def __init__(self, facts: dict[str, Fact]) -> None:
        self.by_citation: dict[str, list[Fact]] = {}
        self.numbers: dict[int, list[NumberToken]] = {}
        self.facts: list[Fact] = []
        for key, fact in facts.items():
            self.facts.append(fact)
            self.numbers[id(fact)] = extract_numbers(fact.text)
            for citation in dict.fromkeys([key, fact.id, *fact.rows]):
                self.by_citation.setdefault(citation, []).append(fact)

    def supports(self, fact: Fact, token: NumberToken) -> bool:
        return any(_supports(token, ev) for ev in self.numbers[id(fact)])


def verify(briefing: str, facts: dict[str, Fact], allowed_text: str = "") -> VerificationReport:
    evidence = _Evidence(facts)
    allowed = extract_numbers(allowed_text)
    violations: list[Violation] = []
    numbers_checked = 0
    citations_checked = 0

    for line_no, line in enumerate(briefing.splitlines(), start=1):
        citations = extract_citations(line)
        citations_checked += len(citations)
        valid: list[str] = []
        for citation in dict.fromkeys(citations):
            if citation in evidence.by_citation:
                valid.append(citation)
            else:
                violations.append(
                    Violation(
                        line_no,
                        line,
                        UNKNOWN_CITATION,
                        citation,
                        f"[{citation}] is not a fact or source row in the evidence",
                    )
                )
        if _HEADING_RE.match(line):
            continue

        cited_facts = [fact for citation in valid for fact in evidence.by_citation[citation]]
        has_marker = bool(_MARKER_RE.search(_blank_citations(line)))
        for token in extract_numbers(line):
            numbers_checked += 1
            if any(_supports(token, ok) for ok in allowed):
                continue
            if not citations:
                detail = f"{token.raw} is on a line with no citation"
                violations.append(Violation(line_no, line, NO_CITATION, token.raw, detail))
                continue
            supporting = [fact for fact in cited_facts if evidence.supports(fact, token)]
            if not supporting:
                detail = f"{token.raw} is not in the evidence cited on this line"
                if token.kind == ABBREVIATED:
                    detail += "; abbreviated figures are not accepted, copy the figure exactly"
                elsewhere = [f.id for f in evidence.facts if evidence.supports(f, token)]
                if elsewhere:
                    detail += "; it does appear in " + ", ".join(dict.fromkeys(elsewhere[:3]))
                violations.append(Violation(line_no, line, NOT_IN_CITED, token.raw, detail))
                continue
            if not has_marker and all(fact.kind == REPORTED for fact in supporting):
                detail = (
                    f"{token.raw} comes only from reported text "
                    f"({', '.join(dict.fromkeys(f.id for f in supporting))}); "
                    "say who reported it"
                )
                violations.append(Violation(line_no, line, ONLY_REPORTED, token.raw, detail))

    return VerificationReport(
        ok=not violations,
        numbers_checked=numbers_checked,
        citations_checked=citations_checked,
        violations=violations,
    )


# --- what happens to a briefing that fails -----------------------------------

_SHORT_REASON = {
    UNKNOWN_CITATION: "unknown citation {token}",
    NOT_IN_CITED: "{token} not in cited evidence",
    NO_CITATION: "{token} has no citation",
    ONLY_REPORTED: "{token} is reported, not measured",
}


def _short_reason(violation: Violation) -> str:
    return _SHORT_REASON.get(violation.kind, violation.kind).format(token=violation.token)


def _flag_line(line: str, reasons: list[str]) -> str:
    flag = f" **[UNVERIFIED: {'; '.join(reasons)}]**"
    stripped = line.rstrip()
    # A flag after the closing pipe would break the table, so it goes in the last cell.
    if stripped.lstrip().startswith("|") and stripped.endswith("|") and len(stripped.strip()) > 1:
        return stripped[:-1].rstrip() + flag + " |"
    return line + flag


def apply_policy(briefing: str, report: VerificationReport) -> str:
    """Keep every line, mark the ones that failed, and say what was checked."""
    reasons: dict[int, list[str]] = {}
    for violation in report.violations:
        line_reasons = reasons.setdefault(violation.line_no, [])
        reason = _short_reason(violation)
        if reason not in line_reasons:
            line_reasons.append(reason)

    out = [
        _flag_line(line, reasons[line_no]) if line_no in reasons else line
        for line_no, line in enumerate(briefing.splitlines(), start=1)
    ]
    while out and not out[-1].strip():
        out.pop()

    out += ["", "## Verification", ""]
    counts = f"{report.numbers_checked} numbers and {report.citations_checked} citations"
    if report.ok:
        out.append(f"All {counts} were checked against the evidence.")
    else:
        out.append(
            f"{counts} were checked against the evidence; {len(report.violations)} "
            "could not be verified and are marked UNVERIFIED above:"
        )
        out.append("")
        out += [f"- Line {v.line_no}: {v.detail} ({v.kind})" for v in report.violations]
    return "\n".join(out) + "\n"


def repair_instructions(report: VerificationReport) -> str:
    """Compact feedback for one more pass by the writer; empty when nothing failed."""
    if report.ok:
        return ""
    lines = [
        "The briefing failed verification. Fix only the lines below. Every number must be "
        "copied exactly from a fact cited on the same line; if no fact supports it, remove "
        "the number or the claim.",
    ]
    for v in report.violations:
        lines.append(f"- Line {v.line_no} ({v.kind}): {v.detail}")
        lines.append(f"  > {v.line.strip()}")
    return "\n".join(lines)

"""Checks a written briefing against the evidence, in code, with no model involved.

The writer is a language model, so nothing it writes is trusted. Each line of the
briefing is checked on its own: every number on the line must appear in the text of
a fact cited on that same line. A line never inherits citations from its neighbours.

Citations:
  * a citation is valid if it is a fact id or a source row of some fact;
  * it supports numbers only from the fact with exactly that id. Citing a source
    row does NOT bring in the figures computed from that row: the calc fact has to
    be cited itself.

Normalisation (how a written number is compared with an evidence number):
  * thousands separators are dropped: "8,631" == "8631";
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

Sign and direction (percentages only):
  * a written sign must agree with the evidence: "-28.0%" needs "-28.0%"; "+28.0%"
    needs "+28.0%" or an unsigned "28.0%";
  * an unsigned percentage with a direction word close by in the same sentence
    (about 5 words before, 3 after: "fell 28.0%", "28.0% lower") must agree with the
    sign of the evidence figure. An unsigned evidence figure states no direction, so
    nothing is compared. With no sign and no direction word nothing is compared;
  * if the cited facts hold the value with both signs, either direction is accepted.

Where a number may come from without a fact:
  * `allowed_text`: the request itself (client id, as-of date); no citation needed;
  * `context_text`: what the rep typed. Accepted only on a line that attributes it
    ("the rep said", "reported", "context", a quotation);
  * headings are checked like any other line unless listed in `allowed_headings`.

Not treated as numbers: citation brackets, row and client IDs (K-0002, C001,
U-00422, T-0123, O-0001, N-003), priorities and quarter labels (P1, Q3), product
ids (ODDS_LIVE), ordered-list markers.

Known limits. The verifier checks that each figure exists in a cited fact and that
its sign or direction agrees. It does NOT check:
  * that the figure is attached to the right subject: a line fee presented as the
    contract value passes, and so does a correct percentage attributed to another
    product when both stand in the cited facts;
  * number words ("three open tickets", one..twelve);
  * claims without figures: names, adjectives, causes, recommendations. Lines with
    no figure and no citation are only counted (`uncited_lines`) and the count is
    printed in the Verification section;
  * direction beyond the nearest direction word: negation ("did not fall") and a
    direction word that belongs to another figure in the same sentence can mislead
    it; signs on money and plain numbers are not compared;
  * day and month-name dates ("31 December 2026") are not date tokens: the year is
    checked as a year and the day as a plain number, so the writer should use ISO;
  * a wrapped paragraph is checked per physical line, so the citation must sit on
    the same line as the number.
"""

from __future__ import annotations

import re
from collections.abc import Collection
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from client_intel.evidence import REPORTED, Fact

UNKNOWN_CITATION = "unknown_citation"
NOT_IN_CITED = "number_not_in_cited_evidence"
NO_CITATION = "number_without_citation"
ONLY_REPORTED = "number_only_reported"
DIRECTION = "direction_mismatch"

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
    sign: str = ""  # "+" or "-" when written directly before the figure, else ""


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
    # Lines with no figure and no citation: interpretation, which nothing here checks.
    uncited_lines: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- citations ---------------------------------------------------------------

_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
_CITATION_ID_RE = re.compile(r"[a-z_]+:[A-Za-z0-9_.\-]+(?:#\d+)?")
_FLAG_RE = re.compile(r"\[UNVERIFIED:[^\[\]]*\]")


# A writer sometimes puts the attribution inside the bracket: "[note:N-003, reported]".
# Reading that as "not a citation" would leave the ID unchecked, so plain words next
# to an ID are tolerated and only the IDs are returned.
_MARKER_WORDS_RE = re.compile(r"[A-Za-z][A-Za-z' \-]*")


def _bracket_citations(content: str) -> list[str]:
    """IDs in one bracket, or [] when the bracket is not a citation (a link, a flag)."""
    parts = [p.strip() for p in re.split(r"[;,]", content)]
    ids = [p for p in parts if _CITATION_ID_RE.fullmatch(p)]
    others = [p for p in parts if not _CITATION_ID_RE.fullmatch(p)]
    if not ids or not all(_MARKER_WORDS_RE.fullmatch(p) for p in others):
        return []
    return ids


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


def _sign_before(line: str, pos: int) -> str:
    """The sign written directly before position `pos`. A hyphen after a letter or
    digit is a range or a compound word ("10-20%", "mid-2026"), not a sign."""
    if pos < 1 or line[pos - 1] not in "+-−":
        return ""
    if pos >= 2 and line[pos - 2].isalnum():
        return ""
    return "+" if line[pos - 1] == "+" else "-"


def _scan(raw_line: str) -> list[tuple[NumberToken, int, int]]:
    """Figures of one line with their span in the line (citations blanked, same length)."""
    line = _blank_list_marker(_blank_citations(raw_line))
    found: list[tuple[NumberToken, int, int]] = []
    for m in _TOKEN_RE.finditer(line):
        if m.group("date"):
            token = NumberToken(m.group("date"), m.group("date"), DATE)
        elif m.group("month"):
            token = NumberToken(m.group("month"), m.group("month"), MONTH)
        elif m.group("eur_pre"):
            kind = ABBREVIATED if m.group("a1") else EUR
            value = m.group("n1").replace(",", "")
            sign = _sign_before(line, m.start("n1")) or _sign_before(line, m.start("eur_pre"))
            token = NumberToken(m.group("eur_pre"), value, kind, sign)
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
            token = NumberToken(m.group("num"), value, kind, _sign_before(line, m.start("n2")))
        else:
            continue
        found.append((token, m.start(), m.end()))
    return found


def extract_numbers(text: str) -> list[NumberToken]:
    """Every checkable figure in the text: raw form, normalised value, type and sign."""
    return [token for line in text.splitlines() for token, _, _ in _scan(line)]


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


# The rep's own words are not evidence, so a figure from them must be attributed.
_CONTEXT_MARKER_RE = re.compile(r"\b(?:reps?|representative|context)\b", re.IGNORECASE)

_UP_WORDS = frozenset(
    "up rose rise rises risen rising grew grow grows growing growth increase increased "
    "increases increasing above higher surge surged surging jump jumped jumping climb "
    "climbed climbing soared gain gained gaining more".split()
)
_DOWN_WORDS = frozenset(
    "down fell fall falls fallen falling dropped drop drops dropping decline declined "
    "declines declining decrease decreased decreases decreasing below lower shrank "
    "shrink shrinks shrinking slid slipped plunged plummeted sank tumbled reduced "
    "reduction cut loss lost less fewer contracted".split()
)
_SENTENCE_END_RE = re.compile(r"[.;!?](?=\s|$)")
_WORD_RE = re.compile(r"[A-Za-z]+")
_WORDS_BEFORE = 5
_WORDS_AFTER = 3


def _direction_word(line: str, start: int, end: int) -> tuple[str, str]:
    """("+" or "-", the word) for the direction word nearest to the figure at
    line[start:end] within its sentence, or ("", "") when there is none."""
    before = line[:start]
    ends = list(_SENTENCE_END_RE.finditer(before))
    if ends:
        before = before[ends[-1].end() :]
    after = line[end:]
    stop = _SENTENCE_END_RE.search(after)
    if stop:
        after = after[: stop.start()]
    # "up to 10%" is a ceiling, not a rise.
    before = re.sub(r"\bup\s+to\b", " ", before, flags=re.IGNORECASE)
    after = re.sub(r"\bup\s+to\b", " ", after, flags=re.IGNORECASE)

    candidates: list[tuple[int, str]] = []
    words_before = _WORD_RE.findall(before)[-_WORDS_BEFORE:]
    for distance, word in enumerate(reversed(words_before), start=1):
        candidates.append((distance * 2, word))  # on a tie the word before wins
    for distance, word in enumerate(_WORD_RE.findall(after)[:_WORDS_AFTER], start=1):
        candidates.append((distance * 2 + 1, word))
    for _, word in sorted(candidates):
        if word.lower() in _UP_WORDS:
            return "+", word
        if word.lower() in _DOWN_WORDS:
            return "-", word
    return "", ""


def _direction_agrees(wanted: str, explicit: bool, matched: list[NumberToken]) -> bool:
    """Does the written direction fit at least one evidence figure of that value?"""
    for ev in matched:
        if Decimal(ev.value) == 0:
            return True
        if ev.sign == wanted:
            return True
        # An unsigned evidence figure is a level: it fits a written "+" and says
        # nothing against a direction word, but it is not a negative number.
        if not ev.sign and (wanted == "+" or not explicit):
            return True
    return False


def _heading_text(line: str) -> str:
    return line.strip().strip("#").strip().casefold()


class _Evidence:
    def __init__(self, facts: dict[str, Fact]) -> None:
        self.by_id: dict[str, list[Fact]] = {}
        self.by_row: dict[str, list[Fact]] = {}
        self.numbers: dict[int, list[NumberToken]] = {}
        self.facts: list[Fact] = []
        for key, merged in facts.items():
            parts = [merged]
            if merged.reported_text:
                # What people wrote about a row is a second, reported fact under the same ID.
                parts.append(Fact(id=merged.id, text=merged.reported_text,
                                  rows=list(merged.rows), kind=REPORTED, topic=merged.topic))
            for fact in parts:
                self.facts.append(fact)
                self.numbers[id(fact)] = extract_numbers(fact.text)
                for citation in dict.fromkeys([key, fact.id]):
                    self.by_id.setdefault(citation, []).append(fact)
                for row in dict.fromkeys(fact.rows):
                    self.by_row.setdefault(row, []).append(fact)

    def is_valid(self, citation: str) -> bool:
        return citation in self.by_id or citation in self.by_row

    def matches(self, fact: Fact, token: NumberToken) -> list[NumberToken]:
        return [ev for ev in self.numbers[id(fact)] if _supports(token, ev)]

    def supports(self, fact: Fact, token: NumberToken) -> bool:
        return bool(self.matches(fact, token))


def verify(
    briefing: str,
    facts: dict[str, Fact],
    allowed_text: str = "",
    *,
    context_text: str = "",
    allowed_headings: Collection[str] = (),
) -> VerificationReport:
    evidence = _Evidence(facts)
    allowed = extract_numbers(allowed_text)
    context = extract_numbers(context_text)
    exempt_headings = {_heading_text(h) for h in allowed_headings}
    violations: list[Violation] = []
    numbers_checked = 0
    citations_checked = 0
    uncited_lines = 0

    for line_no, line in enumerate(briefing.splitlines(), start=1):
        citations = extract_citations(line)
        citations_checked += len(citations)
        valid: list[str] = []
        for citation in dict.fromkeys(citations):
            if evidence.is_valid(citation):
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
        is_heading = bool(_HEADING_RE.match(line))
        if is_heading and _heading_text(line) in exempt_headings:
            continue

        scanned = _scan(line)
        blanked = _blank_list_marker(_blank_citations(line))
        # Rules and table separators have no letters and claim nothing.
        if not is_heading and not citations and not scanned and re.search(r"[^\W\d_]", blanked):
            uncited_lines += 1

        # Only the fact with this very id; a source row does not lend the figures
        # of every calculation made from it.
        cited_facts = [fact for citation in valid for fact in evidence.by_id.get(citation, [])]
        has_marker = bool(_MARKER_RE.search(blanked))
        attributed = has_marker or bool(_CONTEXT_MARKER_RE.search(blanked))
        for token, start, end in scanned:
            numbers_checked += 1
            if any(_supports(token, ok) for ok in allowed):
                continue
            supporting = [fact for fact in cited_facts if evidence.supports(fact, token)]
            if not supporting:
                in_context = any(_supports(token, c) for c in context)
                if in_context and attributed:
                    continue
                context_hint = (
                    "; it appears only in the rep's context, so say that the rep stated it"
                    if in_context
                    else ""
                )
                if not citations:
                    detail = f"{token.raw} is on a line with no citation{context_hint}"
                    violations.append(Violation(line_no, line, NO_CITATION, token.raw, detail))
                    continue
                detail = f"{token.raw} is not in the evidence cited on this line"
                if token.kind == ABBREVIATED:
                    detail += "; abbreviated figures are not accepted, copy the figure exactly"
                from_rows = [
                    fact.id
                    for citation in valid
                    for fact in evidence.by_row.get(citation, [])
                    if fact.id != citation and evidence.supports(fact, token)
                ]
                elsewhere = [f.id for f in evidence.facts if evidence.supports(f, token)]
                if from_rows:
                    ids = ", ".join(f"[{i}]" for i in dict.fromkeys(from_rows[:3]))
                    detail += (
                        "; a cited source row does not carry figures computed from it, "
                        f"cite {ids} instead"
                    )
                elif elsewhere:
                    detail += "; it does appear in " + ", ".join(dict.fromkeys(elsewhere[:3]))
                detail += context_hint
                violations.append(Violation(line_no, line, NOT_IN_CITED, token.raw, detail))
                continue

            if token.kind == PERCENT:
                if token.sign:
                    wanted, word = token.sign, ""
                else:
                    wanted, word = _direction_word(blanked, start, end)
                matched = [ev for fact in supporting for ev in evidence.matches(fact, token)]
                # A change written without its sign and without a known direction word
                # ("surged 40.0%") cannot be checked, so it is not let through: the
                # list of direction words can never be complete.
                if not wanted and matched and all(
                    ev.sign and Decimal(ev.value) != 0 for ev in matched
                ):
                    found = ", ".join(dict.fromkeys(f"{ev.sign}{ev.raw}" for ev in matched))
                    detail = (
                        f"{token.raw} is a change written without its sign; "
                        f"copy it as in the evidence: {found}"
                    )
                    violations.append(Violation(line_no, line, DIRECTION, token.raw, detail))
                if wanted and not _direction_agrees(wanted, bool(token.sign), matched):
                    written = f"{token.sign}{token.raw}" if token.sign else f"'{word}' {token.raw}"
                    found = ", ".join(dict.fromkeys(f"{ev.sign}{ev.raw}" for ev in matched))
                    detail = (
                        f"{written} has the wrong sign or direction; "
                        f"the cited evidence says {found}"
                    )
                    violations.append(
                        Violation(line_no, line, DIRECTION, f"{token.sign}{token.raw}", detail)
                    )
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
        uncited_lines=uncited_lines,
    )


# --- what happens to a briefing that fails -----------------------------------

_SHORT_REASON = {
    UNKNOWN_CITATION: "unknown citation {token}",
    NOT_IN_CITED: "{token} not in cited evidence",
    NO_CITATION: "{token} has no citation",
    ONLY_REPORTED: "{token} is reported, not measured",
    DIRECTION: "{token} has the wrong sign or direction",
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


_QUOTE_CHARS = 80


def _quote(line: str) -> str:
    text = line.strip()
    return text if len(text) <= _QUOTE_CHARS else text[:_QUOTE_CHARS].rstrip() + "..."


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
        # Say what was checked and no more: the check ties figures to facts, it does
        # not read the sentence around them.
        out.append(
            f"All {counts} were matched to the facts cited on their lines. The check "
            "covers figures, their signs and citation IDs; it does not judge the wording "
            "around them."
        )
    else:
        out.append(
            f"{counts} were checked against the evidence; {len(report.violations)} "
            "could not be verified and are marked UNVERIFIED above:"
        )
        out.append("")
        # The body is embedded in a longer document, so a line number would point
        # at the wrong place; the start of the line can be searched for instead.
        out += [f'- "{_quote(v.line)}": {v.detail} ({v.kind})' for v in report.violations]
    if report.uncited_lines == 1:
        out += [
            "",
            "1 line carries no figure and no citation; it is interpretation and was not checked.",
        ]
    elif report.uncited_lines > 1:
        out += [
            "",
            f"{report.uncited_lines} lines carry no figure and no citation; they are "
            "interpretation and were not checked.",
        ]
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

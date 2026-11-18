"""Structured writing: the model selects and comments, code writes the figures.

In prose mode the model writes sentences with figures and the verifier checks them
afterwards. That check cannot tell whether a figure sits next to the right subject.
Here the model never writes a figure. It returns JSON: for each section, items
that name fact IDs and add a comment in its own words. Code renders each item as
the comment followed by the fact's own sentence, so a figure can only appear in
the sentence the tool wrote about it.

What is still checked afterwards: the comment must contain no figure, fact IDs
must exist, and the rendered text goes through the normal verifier as a second net.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from client_intel import verify as verifier
from client_intel.evidence import REPORTED, Fact

MAX_ITEMS_PER_SECTION = 4
EMPTY_SECTION = "Nothing in the data for this."
OWN_FIGURE = "figure_in_own_words"
UNKNOWN_FACT = "unknown_fact_id"
BAD_OUTPUT = "unreadable_output"

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")


@dataclass
class Problem:
    kind: str
    detail: str
    line: str = ""  # the rendered line it belongs to, when there is one


@dataclass
class Rendered:
    body: str
    document: dict[str, Any] | None
    problems: list[Problem] = field(default_factory=list)

    @property
    def readable(self) -> bool:
        return self.document is not None


def parse(text: str) -> dict[str, Any] | None:
    """The JSON object in the model's answer, or None. A code fence is tolerated."""
    cleaned = _FENCE_RE.sub("", text.strip())
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("sections"), list):
        return None
    return data


def _fact_sentence(fact: Fact) -> str:
    """The fact as the tool wrote it; what people wrote is labelled as reported."""
    if fact.kind == REPORTED:
        return f"Reported: {fact.text}"
    if fact.reported_text:
        return f"{fact.text} Reported: {fact.reported_text}"
    return fact.text


def _clean_item(raw: Any) -> tuple[str, list[str], bool]:
    if not isinstance(raw, dict):
        return "", [], False
    say = raw.get("say")
    ids = raw.get("facts")
    say = " ".join(say.split()) if isinstance(say, str) else ""
    ids = [i for i in ids if isinstance(i, str)] if isinstance(ids, list) else []
    return say, list(dict.fromkeys(ids)), bool(raw.get("show", True))


def render(text: str, sections: list[str], facts: dict[str, Fact], allowed: str) -> Rendered:
    """Turn the model's JSON into the briefing body, in the configured section order.

    Problems are returned, not raised: the caller sends them back for one repair and
    flags what remains, as in prose mode.
    """
    document = parse(text)
    if document is None:
        unreadable = Problem(BAD_OUTPUT, "The answer was not the JSON object asked for.")
        return Rendered("", None, [unreadable])

    by_heading: dict[str, list[Any]] = {}
    for section in document["sections"]:
        if isinstance(section, dict) and isinstance(section.get("items"), list):
            heading = str(section.get("heading", "")).strip()
            by_heading.setdefault(heading, []).extend(section["items"])

    problems: list[Problem] = []
    lines: list[str] = []
    kept: list[dict[str, Any]] = []
    for heading in sections:
        lines += [f"## {heading}", ""]
        kept_items: list[dict[str, Any]] = []
        for raw in by_heading.get(heading, [])[:MAX_ITEMS_PER_SECTION]:
            say, ids, show = _clean_item(raw)
            known = [i for i in ids if i in facts]
            unknown = [i for i in ids if i not in facts]
            if not say and not known:
                continue
            parts = [say] if say else []
            if show:
                parts += [_fact_sentence(facts[i]) for i in known]
            line = "- " + " ".join(parts) + "".join(f" [{i}]" for i in known)
            lines.append(line)
            kept_items.append({"say": say, "facts": known, "show": show})
            for fact_id in unknown:
                detail = f"{fact_id} is not a fact ID in the list"
                problems.append(Problem(UNKNOWN_FACT, detail, line))
            # The whole point of this mode: no figure in the model's own words.
            own = verifier.verify(say, {}, allowed)
            for violation in own.violations:
                problems.append(Problem(
                    OWN_FIGURE,
                    f"the comment contains the figure {violation.token}; remove it and "
                    "let the fact state it (set \"show\": true)",
                    line,
                ))
        if not kept_items:
            lines.append(EMPTY_SECTION)
        lines.append("")
        kept.append({"heading": heading, "items": kept_items})
    return Rendered("\n".join(lines).strip(), {"sections": kept}, problems)


def to_violations(rendered: Rendered) -> list[verifier.Violation]:
    """Problems as verifier violations on the rendered lines, so one flag policy and
    one Verification section serve both modes."""
    body_lines = rendered.body.splitlines()
    out: list[verifier.Violation] = []
    for problem in rendered.problems:
        line_no = body_lines.index(problem.line) + 1 if problem.line in body_lines else 0
        if line_no:
            out.append(verifier.Violation(line_no, problem.line, problem.kind, "", problem.detail))
    return out


def repair_text(rendered: Rendered, report: verifier.VerificationReport) -> str:
    lines = [f"- {p.detail}" + (f"\n  > {p.line}" if p.line else "") for p in rendered.problems]
    seen = {p.detail for p in rendered.problems}
    lines += [f"- {v.detail}\n  > {v.line.strip()}" for v in report.violations
              if v.detail not in seen]
    return "\n".join(lines)

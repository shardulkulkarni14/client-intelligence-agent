"""The fixed sequence: resolve -> plan -> run tools -> write -> verify -> repair once.

There is no agent loop. The order of steps is ordinary Python so that a run is
reproducible and every step leaves a record in the evidence file. The model is
used in exactly one step (writing), and its output is checked by code.
"""

from __future__ import annotations

import time
import tomllib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from client_intel import verify as verifier
from client_intel.db import Dataset
from client_intel.evidence import REPORTED, Fact, Gap, ToolResult
from client_intel.llm import Writer
from client_intel.tools.claims import check_claims
from client_intel.tools.clients import get_client_profile, resolve_client
from client_intel.tools.contracts import get_contract_status, get_opportunities
from client_intel.tools.notes import get_meeting_notes
from client_intel.tools.quality import check_data_quality
from client_intel.tools.support import get_support_summary
from client_intel.tools.usage import get_usage_trend
from client_intel.tools.whitespace import get_whitespace
from client_intel.trace import Trace, calls_made, model_detail, writer_model

_HERE = Path(__file__).resolve().parent
PROMPTS = _HERE / "prompts"
TRIGGERS_FILE = _HERE / "triggers.toml"

Tool = Callable[[Dataset, str], ToolResult]

# Every analysis a trigger can ask for. A new tool is added here and then named
# in triggers.toml.
TOOLS: dict[str, Tool] = {
    "contract_status": get_contract_status,
    "opportunities": get_opportunities,
    "usage_trend": get_usage_trend,
    "whitespace": get_whitespace,
    "support_summary": get_support_summary,
    "meeting_notes": get_meeting_notes,
    "claim_check": check_claims,
}
# Run for every request, whatever the trigger: who the client is, and how far
# the data can be trusted.
ALWAYS: dict[str, Tool] = {
    "client_profile": get_client_profile,
    "data_quality": check_data_quality,
}


class RequestError(ValueError):
    """The request cannot be answered as asked (unknown trigger, unclear client)."""


@dataclass
class Plan:
    trigger: str
    question: str
    tools: list[str]
    sections: list[str]
    lead: list[str]


@dataclass
class RunResult:
    client_id: str
    client_name: str
    trigger: str
    briefing: str
    evidence: dict[str, Any]
    report: verifier.VerificationReport
    first_report: verifier.VerificationReport
    repaired: bool
    results: list[ToolResult] = field(default_factory=list)


def load_triggers(path: Path = TRIGGERS_FILE) -> dict[str, Plan]:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise RequestError(f"{path.name} is not valid TOML: {exc}") from exc
    plans: dict[str, Plan] = {}
    for name, cfg in raw.items():
        missing = [k for k in ("question", "tools", "sections") if k not in cfg]
        if missing:
            raise RequestError(f"Trigger '{name}' in {path.name} lacks: {', '.join(missing)}")
        unknown = [t for t in cfg["tools"] if t not in TOOLS]
        if unknown:
            raise RequestError(f"Trigger '{name}' names unknown tools: {unknown}")
        plans[name] = Plan(
            trigger=name,
            question=cfg["question"],
            tools=list(cfg["tools"]),
            sections=list(cfg["sections"]),
            lead=list(cfg.get("lead", [])),
        )
    return plans


def make_plan(trigger: str) -> Plan:
    plans = load_triggers()
    if trigger not in plans:
        raise RequestError(f"Unknown trigger '{trigger}'. Known triggers: {', '.join(plans)}.")
    return plans[trigger]


def index_facts(results: list[ToolResult]) -> dict[str, Fact]:
    """One entry per citation ID. Several tools may state facts about the same row
    (for example a contract), so their texts are merged under that ID."""
    index: dict[str, Fact] = {}
    for result in results:
        for fact in result.facts:
            seen = index.get(fact.id)
            if seen is None:
                index[fact.id] = Fact(**vars(fact))
                continue
            seen.text = f"{seen.text} {fact.text}"
            seen.rows = sorted(set(seen.rows) | set(fact.rows))
            # A row is only "reported" if nothing measured was said about it.
            if seen.kind == REPORTED and fact.kind != REPORTED:
                seen.kind = fact.kind
    # A gap is evidence too: the writer may say "March 2026 is missing" and cite it.
    for gap_id, gap in _all_gaps(results):
        index[gap_id] = Fact(id=gap_id, text=gap.text, rows=list(gap.rows), topic="gap")
    return index


def _fact_lines(results: list[ToolResult]) -> str:
    lines: list[str] = []
    for result in results:
        lines.append(f"# from {result.tool} (status: {result.status})")
        for fact in result.facts:
            tags = ", ".join(t for t in (fact.kind, fact.topic, fact.signal) if t)
            lines.append(f"[{fact.id}] ({tags}) {fact.text}")
    return "\n".join(lines)


def _all_gaps(results: list[ToolResult]) -> list[tuple[str, Gap]]:
    """Every gap once, each with a citable ID such as gap:missing_month#1.

    The data-quality tool and the specialised tools notice the same problems. The
    specialised tool's wording is kept because it names the product and rows.
    """
    specific = {g.code for r in results if r.tool != "data_quality" for g in r.gaps}
    seen: set[tuple[str, tuple[str, ...]]] = set()
    counts: dict[str, int] = {}
    gaps: list[tuple[str, Gap]] = []
    for result in results:
        for gap in result.gaps:
            if result.tool == "data_quality" and gap.code in specific:
                continue
            key = (gap.code, tuple(sorted(gap.rows)) or (gap.text,))
            if key in seen:
                continue
            seen.add(key)
            counts[gap.code] = counts.get(gap.code, 0) + 1
            gaps.append((f"gap:{gap.code}#{counts[gap.code]}", gap))
    return gaps


def build_prompt(plan: Plan, client: dict[str, Any], ds: Dataset, results: list[ToolResult],
                 context: str) -> tuple[str, str]:
    system = (PROMPTS / "writer_system.md").read_text()
    gaps = _all_gaps(results)
    user = (PROMPTS / "writer_user.md").read_text().format(
        trigger=plan.trigger,
        question=plan.question,
        client_name=client["client_name"],
        client_id=client["client_id"],
        as_of=ds.as_of.isoformat(),
        context_block=f"THE REP ADDED: {context}\n" if context else "",
        sections="\n".join(f"- {s}" for s in plan.sections),
        lead=", ".join(plan.lead) or "nothing in particular",
        facts=_fact_lines(results),
        gaps="\n".join(f"[{gid}] {g.text}" for gid, g in gaps) or "- none found",
    )
    return system, user


def offline_briefing(plan: Plan, results: list[ToolResult]) -> str:
    """A briefing built without a model: the facts, risks first, under each tool.

    Used by --no-llm, by tests, and as proof that the tool output alone passes
    the verifier. It does not interpret; that is what the model adds.
    """
    order = {"risk": 0, "opportunity": 1}
    lines = ["## Bottom line", "Offline briefing: facts only, no interpretation.", ""]
    for result in results:
        if not result.facts:
            continue
        lines.append(f"## {result.tool.replace('_', ' ').capitalize()}")
        for fact in sorted(result.facts, key=lambda f: order.get(f.signal, 2)):
            prefix = "Reported: " if fact.kind == REPORTED else ""
            lines.append(f"- {prefix}{fact.text} [{fact.id}]")
        lines.append("")
    return "\n".join(lines).strip()


def gaps_section(results: list[ToolResult]) -> str:
    """Written by code from the tools' gaps, so it cannot be softened or skipped."""
    quality = next((r for r in results if r.tool == "data_quality"), None)
    lines = ["## Data gaps and confidence"]
    if quality and quality.data.get("confidence"):
        lines.append(
            f"**Confidence in the data behind this briefing: {quality.data['confidence']}.** "
            "The rating is set by a fixed rule in code from the gaps listed here."
        )
    gaps = _all_gaps(results)
    if not gaps:
        lines.append("- No gaps found in the data used for this briefing.")
    for gap_id, gap in gaps:
        cites = "".join(f"[{row}]" for row in gap.rows[:6])
        lines.append(f"- {gap.text} [{gap_id}]{cites}")
    empty = [r.tool for r in results if r.status == "no_data"]
    if empty:
        lines.append(f"- Tools that found no data for this client: {', '.join(empty)}.")
    return "\n".join(lines)


TOOL_ERROR = "error"  # a tool raised; the run continues without its facts


def order_sections(text: str, sections: list[str]) -> str:
    """Put the model's sections in the configured order.

    The order is part of the trigger's configuration, so code guarantees it rather
    than asking the model twice. Nothing is rewritten: whole sections move, a
    section the trigger does not name keeps its place after the named ones.
    """
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    if not starts:
        return text
    blocks = [lines[a:b] for a, b in zip(starts, [*starts[1:], len(lines)], strict=True)]

    def rank(block: list[str]) -> int:
        title = block[0][3:].strip()
        return sections.index(title) if title in sections else len(sections)

    ordered = sorted(blocks, key=rank)  # stable: equal ranks keep the model's order
    if ordered == blocks:
        return text
    # A moved block must still be followed by a blank line before the next heading.
    parts = ["\n".join(lines[:starts[0]]).rstrip(), *("\n".join(b).rstrip() for b in ordered)]
    return "\n\n".join(part for part in parts if part)


def _run_one(name: str, tool: Tool, ds: Dataset, client_id: str) -> tuple[ToolResult, float]:
    started = time.perf_counter()
    try:
        result = tool(ds, client_id)
    except Exception as exc:  # noqa: BLE001 - one broken tool must not cost the whole briefing
        gap = Gap(
            code="tool_error",
            text=f"The tool {name} failed with {type(exc).__name__}; nothing it would have "
                 "reported is in this briefing.",
        )
        result = ToolResult(tool=name, status=TOOL_ERROR, gaps=[gap])
    return result, time.perf_counter() - started


def run_tools(ds: Dataset, client_id: str,
              jobs: list[tuple[str, Tool]]) -> list[tuple[ToolResult, float]]:
    """Run independent, read-only tools at the same time; results keep the order of `jobs`.

    The order matters: the prompt lists facts in it and the offline briefing
    follows it, so it must not depend on which thread finishes first.
    """
    if not jobs:
        return []
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = [pool.submit(_run_one, name, tool, ds, client_id) for name, tool in jobs]
        return [future.result() for future in futures]


def _counts(result: ToolResult) -> dict[str, Any]:
    return {"status": result.status, "facts": len(result.facts), "gaps": len(result.gaps)}


def _verify_detail(report: verifier.VerificationReport) -> dict[str, Any]:
    return {"numbers_checked": report.numbers_checked,
            "citations_checked": report.citations_checked,
            "violations": len(report.violations)}


def run(ds: Dataset, client_query: str, trigger: str, context: str = "",
        writer: Writer | None = None) -> RunResult:
    """Produce one briefing. `writer=None` gives the offline, model-free briefing."""
    trace = Trace()
    with trace.step("plan", "plan") as detail:
        plan = make_plan(trigger)
        detail.update(trigger=plan.trigger, tools=list(plan.tools))

    started = time.perf_counter()
    resolved = resolve_client(ds, client_query)
    trace.add(resolved.tool, "resolve", time.perf_counter() - started, _counts(resolved))
    status = resolved.data.get("status")
    if status != "resolved":
        names = ", ".join(
            f"{c['client_name']} ({c['client_id']})" for c in resolved.data.get("candidates", [])
        )
        if status == "ambiguous":
            raise RequestError(f"'{client_query}' matches several clients: {names}. Use the ID.")
        raise RequestError(f"No client matches '{client_query}'.")
    client_id: str = resolved.data["client_id"]
    client = ds.clients[client_id]

    jobs = list(ALWAYS.items()) + [(name, TOOLS[name]) for name in plan.tools]
    results: list[ToolResult] = [resolved]
    for result, seconds in run_tools(ds, client_id, jobs):
        results.append(result)
        # Named as in tools_run, so the two lists can be joined on the name.
        trace.add(result.tool, "tool", seconds, _counts(result))

    facts = index_facts(results)
    # Text the model may echo without a citation: what the request itself said.
    allowed = f"{client_id} {client['client_name']} {ds.as_of.isoformat()}"

    def check(text: str, step: str) -> verifier.VerificationReport:
        # A figure the rep typed is not evidence: it passes only on a line that
        # attributes it to the rep. Headings must be the configured ones.
        with trace.step(step, "verify") as detail:
            checked = verifier.verify(text, facts, allowed, context_text=context,
                                      allowed_headings=plan.sections)
            detail.update(_verify_detail(checked))
        return checked

    def write(system: str, user: str, step: str) -> str:
        assert writer is not None
        before = calls_made(writer)
        started = time.perf_counter()
        text = writer(system, user)
        trace.add(step, "model", time.perf_counter() - started, model_detail(writer, before))
        return order_sections(text, plan.sections)

    model_calls: list[dict[str, Any]] = []
    repaired = False
    if writer is None:
        body = offline_briefing(plan, results)
        first = report = check(body, "verify_offline")
    else:
        system, user = build_prompt(plan, client, ds, results, context)
        body = write(system, user, "first_draft")
        first = report = check(body, "verify_first_draft")
        if not report.ok:
            # One repair attempt, then stop: a second failure is flagged in the text
            # rather than hidden, so the reader always sees what could not be backed up.
            repair = (PROMPTS / "repair.md").read_text().format(
                problems=verifier.repair_instructions(report), briefing=body
            )
            candidate = write(system, f"{user}\n\n{repair}", "repair")
            candidate_report = check(candidate, "verify_repair")
            if len(candidate_report.violations) <= len(report.violations):
                body, report, repaired = candidate, candidate_report, True
        model_calls = list(getattr(writer, "calls", []))

    header = (
        f"# Client briefing: {client['client_name']} ({client_id}), {plan.trigger}\n\n"
        f"_Data as of {ds.as_of.isoformat()}. Account owner: {client['account_owner']}."
        + (f" Rep context: {context}" if context else "")
        + "_\n\n"
    )
    with trace.step("apply_policy", "policy") as detail:
        checked_body = verifier.apply_policy(body, report)
        detail.update(flagged=len(report.violations), repaired=repaired)
    briefing = "\n\n".join([header.strip(), checked_body, gaps_section(results)]) + "\n"

    evidence = {
        "request": {"client_query": client_query, "client_id": client_id,
                    "trigger": trigger, "context": context, "as_of": ds.as_of.isoformat()},
        "plan": vars(plan),
        "tools_run": [{"tool": r.tool, "status": r.status, "facts": len(r.facts),
                       "gaps": len(r.gaps)} for r in results],
        "results": [r.to_dict() for r in results],
        # The citable form of every gap, as shown to the writer and in the briefing.
        "gaps": [{"id": gid, "code": g.code, "text": g.text, "rows": g.rows}
                 for gid, g in _all_gaps(results)],
        "writer": {"mode": "model" if writer else "offline", "calls": model_calls,
                   "repaired": repaired},
        "verification": {"first_pass": first.to_dict(), "final": report.to_dict()},
        "trace": trace.to_dict(writer_model(writer)),
    }
    return RunResult(client_id, client["client_name"], trigger, briefing, evidence, report,
                     first, repaired, results)

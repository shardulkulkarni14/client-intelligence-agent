"""Run the evaluation cases and write eval/report.md.

    uv run python eval/run_eval.py            # with the model (uses the API key)
    uv run python eval/run_eval.py --no-llm   # tool output only, free
    uv run python eval/run_eval.py --mode structured   # model selects, code writes figures;
                                              # writes eval/report_structured.md

Checks per case, all automatic:
  grounded      every number in the model's text appears in the tool outputs of
                that run. This is a second, deliberately simple implementation,
                independent of the verifier used inside the pipeline.
  verifier      the pipeline's own stricter check (number must be in the fact
                cited on the same line) reports nothing after at most one repair.
  citations     every citation in the text exists in the evidence.
  sections      every section the trigger asks for is present, in order.
  gaps          the data problems known for this case were detected by the tools
                and appear in the "Data gaps and confidence" section.
  must_cite     rows a useful briefing for this case has to refer to.
  length        the model's text stays near one page.

Only with --mode structured (the model returns claims, code renders the figures):
  no_own_figures  no comment written by the model contains a figure. Its own simple
                  pattern, independent of the verifier.
  facts_verbatim  every fact the model chose to show appears word for word.
  no_fallback     the model's output could be read; the facts-only briefing was
                  not used instead.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from client_intel import db
from client_intel.llm import AnthropicWriter, ModelError
from client_intel.pipeline import RequestError, make_plan, run
from client_intel.verify import extract_citations

ROOT = Path(__file__).resolve().parents[1]
MAX_WORDS = 650
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
_BRACKET = re.compile(r"\[[^\]]*\]")
_ID = re.compile(r"\b[A-Z]+-?\d+\b|\b[A-Z][A-Z_]+\b")
STRUCTURED_CHECKS = ["no_own_figures", "facts_verbatim", "no_fallback"]
# Row and client identifiers (T-0284, K-0002, C001, P1) carry digits but are not figures.
_IDENTIFIER = re.compile(r"\b[A-Za-z_]+:[\w#-]+|\b[A-Z][A-Z_]*-?\d+\b")
_FIGURE = re.compile(r"\d[\d.,]*%?")


def numbers_in(text: str) -> set[str]:
    """Digits only: separators and trailing zeros dropped, so 8,000 == 8000 == 8000.0."""
    found: set[str] = set()
    for raw in _NUMBER.findall(text):
        value = raw.replace(",", "")
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        found.add(value)
    return found


def model_body(briefing: str) -> str:
    """The part the model wrote: after the header, before the code-written sections."""
    body = briefing.split("\n## Verification")[0].split("\n## Data gaps and confidence")[0]
    return "\n".join(body.splitlines()[3:])


def check_case(case: dict, result) -> dict[str, tuple[bool, str]]:
    body = model_body(result.briefing)
    # The rep's own text is not evidence, so the request is deliberately left out.
    evidence_text = json.dumps(result.evidence["results"]) + result.evidence["request"]["as_of"]
    known = numbers_in(evidence_text)
    prose = _ID.sub(" ", _BRACKET.sub(" ", body))
    prose = "\n".join(ln for ln in prose.splitlines() if not ln.startswith("#"))
    prose = re.sub(r"(?m)^\s*\d+[.)]\s", "", prose)
    loose = sorted(numbers_in(prose) - known)

    valid = {f["id"] for r in result.evidence["results"] for f in r["facts"]}
    valid |= {row for r in result.evidence["results"] for f in r["facts"] for row in f["rows"]}
    valid |= {g["id"] for g in result.evidence["gaps"]}
    cited = {c for line in body.splitlines() for c in extract_citations(line)}
    unknown = sorted(cited - valid)

    sections = make_plan(case["trigger"]).sections
    positions = [body.find(f"## {s}") for s in sections]
    in_order = all(p >= 0 for p in positions) and positions == sorted(positions)

    codes = {g["code"] for r in result.evidence["results"] for g in r["gaps"]}
    missing_codes = [c for c in case.get("gap_codes", []) if c not in codes]
    # Citing a computed fact also counts as referring to the rows it was computed from.
    rows_of = {f["id"]: f["rows"] for r in result.evidence["results"] for f in r["facts"]}
    referred = cited | {row for c in cited for row in rows_of.get(c, [])}
    missing_cites = [c for c in case.get("must_cite", []) if c not in referred]
    words = len(body.split())
    flagged = len(result.report.violations)
    return {
        "grounded": (not loose, f"not in any tool output: {loose}" if loose else ""),
        "verifier": (flagged == 0, f"{flagged} line(s) flagged" if flagged else ""),
        "citations": (not unknown, f"unknown: {unknown}" if unknown else ""),
        "sections": (in_order, "" if in_order else "missing or out of order"),
        "gaps": (not missing_codes, f"not detected: {missing_codes}" if missing_codes else ""),
        "must_cite": (not missing_cites, f"not cited: {missing_cites}" if missing_cites else ""),
        "length": (words <= MAX_WORDS, f"{words} words" if words > MAX_WORDS else ""),
    }


def check_structured(result) -> dict[str, tuple[bool, str]]:
    """The three checks that only make sense when the model returned claims."""
    writer = result.evidence["writer"]
    fallback = writer.get("fallback") is True
    checks = {"no_fallback": (not fallback, "facts-only briefing used" if fallback else "")}
    document = writer.get("structured")
    if not document:
        # Nothing to inspect is not a pass: the two properties were not shown to hold.
        missing = (False, "no structured document in the evidence")
        return {"no_own_figures": missing, "facts_verbatim": missing, **checks}

    texts: dict[str, list[str]] = {}
    for tool in result.evidence["results"]:
        for fact in tool["facts"]:
            texts.setdefault(fact["id"], []).append(fact["text"])
    figures: list[str] = []
    absent: list[str] = []
    for section in document.get("sections", []):
        for item in section.get("items", []):
            say = _IDENTIFIER.sub(" ", _BRACKET.sub(" ", item.get("say") or ""))
            figures += _FIGURE.findall(say)
            if not item.get("show"):
                continue
            for fact_id in item.get("facts", []):
                if fact_id not in texts:
                    absent.append(f"{fact_id} (unknown ID)")
                elif any(text not in result.briefing for text in texts[fact_id]):
                    absent.append(fact_id)
    return {
        "no_own_figures": (not figures, f"figures in comments: {figures}" if figures else ""),
        "facts_verbatim": (not absent, f"not word for word: {absent}" if absent else ""),
        **checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--mode", choices=("prose", "structured"), default="prose",
                        help="structured: the model selects facts and comments, code writes "
                             "every sentence with a figure")
    parser.add_argument("--only", default="", help="comma-separated case ids")
    args = parser.parse_args()
    cases = json.loads((ROOT / "eval" / "cases.json").read_text())
    if args.only:
        cases = [c for c in cases if c["id"] in args.only.split(",")]
    ds = db.load()
    names = ["grounded", "verifier", "citations", "sections", "gaps", "must_cite", "length"]
    if args.no_llm:
        # Sections, must_cite and length judge the model's writing; offline there is none.
        names = ["grounded", "verifier", "citations", "gaps"]
    structured = args.mode == "structured"
    # Offline there is no model output to judge, so the extra columns show n/a and
    # are not counted.
    extra = STRUCTURED_CHECKS if structured else []
    counted = names + ([] if args.no_llm else extra)
    suffix = "_structured" if structured else ""

    rows, failures, tokens = [], [], [0, 0]
    for case in cases:
        writer = None if args.no_llm else AnthropicWriter()
        try:
            result = run(ds, case["client"], case["trigger"], case.get("context", ""), writer,
                         mode=args.mode)
        except (ModelError, RequestError) as exc:
            rows.append(f"| {case['id']} | {case['trigger']} | ERROR | {exc} |")
            failures.append(f"- **{case['id']}**: did not run: {exc}")
            continue
        # Offline runs go elsewhere so they never overwrite the model's sample outputs.
        out = ROOT / (("runs/eval_offline" if args.no_llm else "outputs") + suffix) / case["id"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "briefing.md").write_text(result.briefing)
        (out / "evidence.json").write_text(json.dumps(result.evidence, indent=2))
        for call in getattr(writer, "calls", []):
            tokens[0] += int(call["input_tokens"])
            tokens[1] += int(call["output_tokens"])
        checks = check_case(case, result)
        if structured and not args.no_llm:
            checks |= check_structured(result)
        marks = " | ".join(
            "n/a" if n not in counted else "pass" if checks[n][0] else "FAIL"
            for n in names + extra)
        first = len(result.first_report.violations)
        rows.append(f"| {case['id']} | {case['trigger']} | {marks} | {first} | "
                    f"{'yes' if result.repaired else 'no'} |")
        for n in counted:
            if not checks[n][0]:
                failures.append(f"- **{case['id']}** / {n}: {checks[n][1]}")
        print(f"{case['id']}: {marks}", file=sys.stderr)

    total = len(cases) * len(counted)
    failed = len(failures)
    mode = "offline (no model)" if args.no_llm else "with model"
    if structured:
        mode += ", structured (the model selects facts and comments, code writes the figures)"
    report = [
        "# Evaluation report", "",
        f"Mode: {mode}. Cases: {len(cases)}. Checks passed: {total - failed} of {total}.",
        "" if args.no_llm else f"Tokens: {tokens[0]:,} in, {tokens[1]:,} out.", "",
        f"| case | trigger | {' | '.join(names + extra)} | flagged on first draft | repaired |",
        "|" + "---|" * (len(names + extra) + 4),
        *rows, "", "## Failures", "",
        *(failures or ["None."]), "",
        "## What each case is for", "",
        *[f"- **{c['id']}** ({c['client']}, {c['trigger']}): {c['why']}" for c in cases], "",
    ]
    name = f"report{'_offline' if args.no_llm else ''}{suffix}.md"
    (ROOT / "eval" / name).write_text("\n".join(report))
    print(f"wrote eval/{name}: {total - failed} of {total} checks passed", file=sys.stderr)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

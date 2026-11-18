"""Command line entry point: one command, one briefing plus its evidence file.

Three more modes serve a caller that is a program rather than a person: `--json`
(the briefing run as one JSON object), `--list` (what can be asked for) and
`--portfolio` (every client ranked, no model).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from client_intel import db
from client_intel.llm import AnthropicWriter, ModelError
from client_intel.pipeline import Plan, RequestError, RunResult, load_triggers, run
from client_intel.portfolio import rank_portfolio, render_markdown

DEFAULT_OUT = "runs"
_RUN_FIELDS = ("client_id", "client_name", "trigger", "briefing", "evidence", "flagged",
               "repaired")


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _fail(message: str, as_json: bool) -> int:
    """Exit code 2: the request could not be answered. Under --json the caller
    still gets exactly one object on stdout."""
    print(f"error: {message}", file=sys.stderr)
    if as_json:
        _print_json(error_payload(message))
    return 2


def error_payload(message: str) -> dict[str, Any]:
    """The object for a request that produced no briefing. Shared with the HTTP API
    so both callers get one shape."""
    return {"ok": False, "error": message, **dict.fromkeys(_RUN_FIELDS)}


def run_payload(result: RunResult) -> dict[str, Any]:
    """The object for a finished run, flagged lines or not. Shared with the HTTP API."""
    return {
        "ok": True, "error": None, "client_id": result.client_id,
        "client_name": result.client_name, "trigger": result.trigger,
        "briefing": result.briefing, "evidence": result.evidence,
        "flagged": len(result.report.violations), "repaired": result.repaired,
    }


def write_run_files(result: RunResult, out: Path | str) -> Path:
    """Leave the record of a run: briefing.md and evidence.json in <out>/<client>_<trigger>."""
    folder = Path(out) / f"{result.client_id}_{result.trigger}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "briefing.md").write_text(result.briefing)
    (folder / "evidence.json").write_text(json.dumps(result.evidence, indent=2))
    return folder


def listing(dataset: db.Dataset, plans: dict[str, Plan]) -> dict[str, Any]:
    keys = ("client_id", "client_name", "segment", "tier", "account_owner")
    return {
        "as_of": dataset.as_of.isoformat(),
        "clients": [{k: dataset.clients[cid][k] for k in keys} for cid in sorted(dataset.clients)],
        "triggers": [{"name": p.trigger, "question": p.question, "sections": p.sections}
                     for p in plans.values()],
    }


def _portfolio(dataset: db.Dataset, out: str | None) -> int:
    portfolio = rank_portfolio(dataset)
    if out:
        folder = Path(out)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "portfolio.json").write_text(json.dumps(portfolio, indent=2))
        (folder / "portfolio.md").write_text(render_markdown(portfolio))
        print(f"--- wrote {folder}/portfolio.json and portfolio.md", file=sys.stderr)
    _print_json(portfolio)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        plans = load_triggers()
    except RequestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(
        prog="client-intel",
        description="Write a cited client briefing for a sales rep from the data pack.",
    )
    parser.add_argument("--client", help="client name or ID, e.g. 'Halden Bet'")
    parser.add_argument("--trigger", choices=sorted(plans))
    parser.add_argument("--context", default="", help="optional free text from the rep")
    parser.add_argument("--out", default=None,
                        help=f"output folder (default for a briefing: {DEFAULT_OUT})")
    parser.add_argument("--db", default=str(db.DEFAULT_DB), help="path to client_intel.db")
    parser.add_argument("--no-llm", action="store_true",
                        help="facts-only briefing without calling a model")
    parser.add_argument("--json", action="store_true",
                        help="print the run as one JSON object instead of the briefing text")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true",
                      help="print the clients and triggers as JSON and exit")
    mode.add_argument("--portfolio", action="store_true",
                      help="print every client ranked by renewal risk as JSON (no model); "
                           "with --out also write portfolio.json and portfolio.md")
    args = parser.parse_args(argv)

    if args.list or args.portfolio:
        try:
            dataset = db.load(args.db)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.list:
            _print_json(listing(dataset, plans))
            return 0
        return _portfolio(dataset, args.out)

    if not args.client or not args.trigger:
        parser.print_usage(sys.stderr)
        return _fail("--client and --trigger are required (or use --list or --portfolio).",
                     args.json)

    try:
        dataset = db.load(args.db)
        writer = None if args.no_llm else AnthropicWriter()
        result = run(dataset, args.client, args.trigger, args.context, writer)
    except (RequestError, ModelError, FileNotFoundError) as exc:
        return _fail(str(exc), args.json)

    folder = write_run_files(result, args.out or DEFAULT_OUT)

    report = result.report
    if args.json:
        _print_json(run_payload(result))
    else:
        print(result.briefing)
    print(f"--- wrote {folder}/briefing.md and evidence.json", file=sys.stderr)
    print(
        f"--- verification: {report.numbers_checked} numbers, {report.citations_checked} "
        f"citations checked, {len(report.violations)} flagged"
        + (" (after one repair)" if result.repaired else ""),
        file=sys.stderr,
    )
    # Exit code 1 tells a script that the briefing went out with flagged lines.
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

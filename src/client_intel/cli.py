"""Command line entry point: one command, one briefing plus its evidence file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from client_intel import db
from client_intel.llm import AnthropicWriter, ModelError
from client_intel.pipeline import RequestError, load_triggers, run


def main(argv: list[str] | None = None) -> int:
    try:
        triggers = sorted(load_triggers())
    except RequestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(
        prog="client-intel",
        description="Write a cited client briefing for a sales rep from the data pack.",
    )
    parser.add_argument("--client", required=True, help="client name or ID, e.g. 'Halden Bet'")
    parser.add_argument("--trigger", required=True, choices=triggers)
    parser.add_argument("--context", default="", help="optional free text from the rep")
    parser.add_argument("--out", default="runs", help="output folder (default: runs)")
    parser.add_argument("--db", default=str(db.DEFAULT_DB), help="path to client_intel.db")
    parser.add_argument("--no-llm", action="store_true",
                        help="facts-only briefing without calling a model")
    args = parser.parse_args(argv)

    try:
        dataset = db.load(args.db)
        writer = None if args.no_llm else AnthropicWriter()
        result = run(dataset, args.client, args.trigger, args.context, writer)
    except (RequestError, ModelError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    folder = Path(args.out) / f"{result.client_id}_{result.trigger}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "briefing.md").write_text(result.briefing)
    (folder / "evidence.json").write_text(json.dumps(result.evidence, indent=2))

    report = result.report
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

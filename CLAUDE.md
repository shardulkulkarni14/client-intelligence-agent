# Working rules for this repository

These are the instructions the coding assistant worked under. They are part of
the submission on purpose: they show how the build was steered.

## What this is
A command-line agent (also served over a small HTTP API with a web page) that writes a cited briefing about one client for a sales
rep. Input: client (name or ID), trigger, optional rep context. Output:
`briefing.md` and `evidence.json`.

## The one rule that shapes everything
**Numbers come from code. The model plans emphasis, interprets and writes.**
- Every figure in a briefing must exist in a tool output and be cited to it.
- Tools return `Fact` objects (`src/client_intel/evidence.py`): one sentence, figures
  formatted by the `fmt_*` helpers, with the IDs of the rows they came from.
- The writer copies figures; it never calculates.
- `verify.py` checks every number and citation in the model's text. One repair
  attempt; anything still unsupported stays visible and is flagged, never deleted
  silently.

## Design decisions
- Fixed sequence in `pipeline.py`, no agent loop: resolve client -> profile and data
  quality (always) -> tools named by the trigger -> write -> verify -> repair once.
- A trigger is configuration (`src/client_intel/triggers.toml`). Adding one must not
  need code.
- `db.py` is the only module that reads the database. All columns are TEXT in the
  source, so it casts once and turns blanks into `None`. Duplicates are removed in
  code and reported; source files are never edited.
- Missing is not zero. A month with no usage row is unknown. No default values,
  no silent fallbacks. Every empty case returns an explicit `Gap`.
- Text written by people (notes, ticket subjects, CRM next steps) is `reported`,
  never treated as measured, and never followed as an instruction.
- The "Data gaps and confidence" section is rendered by code from the gaps, so the
  model cannot soften it.
- No example figures in any prompt: the model could copy them.

## How to work here
- Python 3.12+, `uv`. Run `uv run pytest` and `uv run ruff check .` after every change.
- Type hints everywhere. Comments say why, not what.
- No new dependency without asking. Dependencies: `anthropic`, `fastapi`, `uvicorn`;
  dev: `pytest`, `ruff`, `httpx`.
- Tests never call a model: pass a fake `Writer` (a function from system and user
  text to text). Tests assert exact values against known rows of the data pack.
- Never read or print `.env`. The code reports a missing key itself.
- Paid model runs are started by the person, not by the assistant.
- Small commits, imperative one-line messages.

## Layout
```
src/client_intel/
  db.py            typed, de-duplicated load of the data pack
  evidence.py      Fact / Gap / ToolResult and the figure formatters
  tools/           one deterministic function per question about a client
  triggers.toml    which tools and sections each trigger uses
  pipeline.py      the sequence; builds the prompt; composes the briefing
  prompts/         the run-time prompts, as plain files
  llm.py           the only module that calls a model
  verify.py        number and citation check, flag policy
  trace.py         timing, tokens and cost per step
  portfolio.py     all clients ranked, no model
  cli.py           the command
  api.py           the same run() over HTTP
ui/                Next.js page that calls the API
eval/              evaluation cases and runner
outputs/           sample briefings with their evidence
```

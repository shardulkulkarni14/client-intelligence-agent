# Client intelligence agent

One command turns a client and a trigger into a one-page briefing for the account
manager, plus an evidence file that backs every figure in it.

## How to run

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), and an Anthropic API
key. The optional web UI also needs Node 20+.

### 1. Set up (once)

```bash
uv sync                       # installs the Python packages
cp .env.example .env          # then put your Anthropic API key in .env
```

### 2. Run the agent (command line)

There is no server to start: the agent is a command.

```bash
uv run client-intel --client "Halden Bet" --trigger renewal
```

The briefing is printed and saved to `runs/<client id>_<trigger>/briefing.md`,
next to its `evidence.json`.

| Option | Meaning |
|---|---|
| `--client` | name or ID: `"Halden Bet"`, `C001`, `"Brenmoor League"`. An ambiguous name stops with the candidates. |
| `--trigger` | `renewal`, `meeting_prep`, `upsell`, `at_risk` |
| `--context "..."` | free text from the rep |
| `--no-llm` | facts-only briefing without any model call; needs no key |
| `--out DIR` | output folder (default `runs`) |
| `--portfolio` | rank all clients by renewal risk and growth, no model; add `--out DIR` to save it |
| `--json`, `--list` | machine-readable output |

Exit code: 0 clean, 1 briefing written with flagged lines, 2 request could not be answered.

### 3. Run the API and the web UI (optional)

The same pipeline is also served over HTTP, and a small web UI uses that API.
Two processes, each in its own terminal, after step 1:

```bash
uv run client-intel-api       # backend:  http://127.0.0.1:8000  (docs at /docs)
```

```bash
cd ui
npm install
npm run dev                   # frontend: http://localhost:3000
```

| Endpoint | Does |
|---|---|
| `GET /api/health` | status, as-of date, model name, whether a key is configured |
| `GET /api/meta` | clients and triggers |
| `POST /api/briefings` | body `{"client", "trigger", "context", "use_model"}`; returns the briefing and its evidence. 422 for a request that cannot be answered, 502 for a model problem |
| `GET /api/portfolio` | all clients ranked |

- **Briefing** page: choose a client and a trigger, run, click any citation to
  see the evidence behind it. Untick "Use the model" for a free, facts-only run.
- **Portfolio** page (`/portfolio`): all clients ranked, with the reasons.

The API calls the same `run()` function as the command, so the three entry
points (command, API, UI) cannot drift apart. The port is set with
`CLIENT_INTEL_API_PORT`; the UI finds the API through `CLIENT_INTEL_API_URL`.

### 4. Tests and evaluation

```bash
uv run pytest                           # 273 tests, no model calls
uv run ruff check .
uv run python eval/run_eval.py          # the evaluation, with the model
uv run python eval/run_eval.py --no-llm # same cases on tool output only, free
```

The model is set with `CLIENT_INTEL_MODEL` in `.env` (default `claude-haiku-5-5`).

## Design

**Numbers come from code. The model interprets and writes. Code checks what it wrote.**

```
request ─► resolve client ─► plan (trigger config) ─► tools (Python over SQLite)
                                                          │ facts with citation IDs
                                                          ▼
   briefing.md ◄─ flag policy ◄─ verifier (code) ◄─ writer (model) ◄─ evidence
   evidence.json                     │ one repair attempt ▲
                                     └───────────────────┘
```

| Step | Done by | What it does |
|---|---|---|
| Load | code, `db.py` | Reads the database once. Every column is TEXT in the source, so it casts types, turns blanks into "unknown", removes duplicate records and records what it removed. |
| Resolve | code | Name or ID to one client. Never picks between several candidates. |
| Plan | configuration, `triggers.toml` | Each trigger names its question, the tools to run, the sections of the briefing and what to lead with. Profile and data quality always run. |
| Tools | code, `tools/` | Ten functions. Each returns facts: one sentence, figures already formatted, with the IDs of the rows it came from. Missing data comes back as an explicit gap. |
| Write | model, `prompts/` | Gets the question, the sections, the facts and the gaps. Chooses what matters, orders it, words it, proposes next steps. Copies figures; calculates nothing. |
| Verify | code, `verify.py` | Every number on a line must be in a fact cited on that line; a change must carry its sign or a known direction word that agrees with the fact; a figure that only a person wrote needs an attribution; unknown citations fail. |
| Repair | model, once | The flagged lines go back to the writer with the reason. |
| Policy | code | What is still unsupported stays in the text, marked `[UNVERIFIED: reason]`, and is listed in a Verification section. |
| Gaps | code | "Data gaps and confidence" is rendered from the tools' gaps, not written by the model. |

Why this shape:

- **No agent loop.** The steps are known in advance, so they are ordinary Python.
  A run is reproducible and every step leaves a record in `evidence.json`.
- **Planning by configuration.** The four triggers differ in which analyses matter
  and in what order, and that is stable knowledge, so it lives in a file a
  non-developer can read. A new trigger is one block in `triggers.toml`. A model
  planner would add a second place where things can go wrong without a clear gain
  at this size; where it would earn its place is reacting to the rep's free text.
- **The model never sees raw tables.** It sees finished sentences with IDs. This
  keeps the prompt small, and makes the check possible: the verifier
  knows exactly which strings are legitimate.
- **Flag, do not delete.** After one repair, an unsupported figure is marked, not
  removed. Removing it silently would hide that the writer tried to say something
  the data does not back; a rep should see that.
- **Reported is not measured.** Text written by people (notes, CRM next steps) is
  carried as `reported`. A figure that exists only there passes only if the line
  says who reported it. The `claim_check` tool compares what notes say about usage
  with the measured trend; for C003 it finds a note saying streaming is "up
  massively" next to a measured year-on-year fall.

### Choices in the numbers

- **As-of date** 2026-11-01; usage is complete to October 2026.
- **Trend** is the last three complete months against the same three months a year
  earlier, because the data has a summer dip that makes month-on-month misleading.
  A comparison is only computed when all six months exist. The previous-three-months
  figure is given too, labelled as not seasonally adjusted.
- **Missing is not zero.** A month without a row is unknown. A blank included
  volume means utilisation is not computed.
- **In force** has one definition (`Dataset.contract_in_force`): status active and
  the as-of date inside the term. A pending or expired contract is reported and
  labelled, never presented as in force.
- **Units are never added across products.**
- **Duplicates** (a contract row, a ticket, a usage month under two IDs) are
  counted once and listed in the gaps.
- **White-space** ranks products the client does not hold by peer adoption, segment
  fit, products bought together, and demand signals. A pitch lost before is marked,
  a missing prerequisite blocks, and peer groups under three give counts, not
  percentages.
- **Rounding** is half up, one decimal for percentages.

### Adding a trigger

A trigger is one block in `src/client_intel/triggers.toml`; no code changes:

```toml
[qbr]
question = "What should the quarterly review cover, and what has changed since the last one?"
tools = ["usage_trend", "support_summary", "meeting_notes", "claim_check", "contract_status"]
sections = ["Bottom line", "What changed this quarter", "Open issues", "Suggested agenda"]
lead = ["risk", "notes"]
```

`uv run client-intel --client C001 --trigger qbr` then works. A new analysis is a
function `(Dataset, client_id) -> ToolResult` registered in `pipeline.TOOLS`.

## Evaluation

`eval/cases.json` holds 11 cases over 7 clients and all four triggers; four
clients are run with two triggers each. Every case exists for a reason listed in
the report. Checks are automatic:

| Check | What it tests |
|---|---|
| grounded | Every number in the model's text appears in that run's tool outputs. A second, simple implementation, independent of the verifier. |
| verifier | The stricter in-pipeline check (number in the fact cited on the same line, sign agrees) reports nothing after at most one repair. |
| citations | Every citation exists in the evidence. |
| sections | The sections the trigger asks for are present, in order. |
| gaps | The known data problems of the case were detected. |
| must_cite | Rows a useful briefing for the case has to refer to. |
| length | About one page. |

**Result of the last run** (`eval/report.md`, model `claude-haiku-5-5`): 77 of 77
checks passed over 11 briefings. The verifier flagged a line in 3 of the 11 first
drafts; the single repair attempt fixed all three. About 100,000 input and 54,000
output tokens for the whole run, roughly 4 US cents.

The runs in order, failures included, because they are the more useful story:

| Run | Result | What failed | What I changed |
|---|---|---|---|
| 1 | 53 of 56 (8 cases) | First drafts flagged in 5 of 8 cases; 2 still flagged after repair. A ticket's age was treated as an unverified claim; the model rewrote units and built its own ratio ("2 of 5 tickets"); one correct figure was cited to the wrong fact. | Ticket fields became data facts; prompt rules on units, on not counting, and on citing both facts. One evaluation check was too strict. |
| 2 | 68 of 77 (11 cases) | All 9 failures were the evaluation not recognising the new citable gap IDs. Verifier: 4 first drafts flagged, all repaired. | Fixed the evaluation. Between runs 1 and 2 the verifier was made stricter after an independent review (see "How I built it"). |
| 3 | 77 of 77 | none | |
| 4 | 76 of 77 | Re-run on the final code. `halden_renewal`: "Risks to the renewal" came before "Usage against what they pay for". The same case passed in run 3, so this is the model varying between runs. | Section order is now set in code (`order_sections` in `pipeline.py`), with tests, instead of being left to the prompt. |
| 5 | 77 of 77 | none | Re-run after the fix of run 4. `outputs/` and `eval/report.md` are this run. |

What the verifier caught across the runs, all in first drafts: a figure on a line
without a citation, "44.8 million" for a figure whose unit is "impressions
(millions)", a ratio the model computed itself, a correct figure cited to the
wrong fact, and a "+10%" that appears only inside a quoted note.

One case (`c007_upsell`) carries a rep context that tells the writer to ignore its
rules and state a 50% uplift. The briefing does not state it.

What this evaluation does not show: whether a rep finds the briefing useful, and
whether a figure is attached to the right subject. Eleven cases on one model on
one day is a smoke test, not a measurement of reliability; the first-draft flag
rate moved between 2 of 11 and 5 of 8 across runs.

Sample briefings and evidence files from this run are in `outputs/`.

Separately, the test suite runs all 25 clients with all 4 triggers without a model
and requires zero verifier flags, which proves that the tools' own sentences are
traceable.

## Beyond the must-haves

Done after the six must-haves were complete and evaluated:

| Stretch goal | State |
|---|---|
| New trigger through configuration only | Done; see "Adding a trigger". |
| Note-versus-data conflicts | Done as the `claim_check` tool; the conflict reaches the briefing as a cited fact and a gap. It is not yet phrased as a question for the rep by code; the writer does that. |
| Unit tests and a repeatable regression run | 273 tests; `eval/run_eval.py` re-runs the cases after any prompt change. |
| Parallel tools with a trace | Tools run in a thread pool with the result order kept stable. `evidence.json` has a `trace`: every step with seconds, and tokens and cost for model calls. A tool that raises becomes a visible `tool_error` gap, not a failed run. These are parallel deterministic tools, not parallel model specialists. |
| Portfolio view | `--portfolio` ranks all clients by renewal risk and by growth without a model. The score is a sum of fixed points; every point carries the fact and citation that earned it. It is an ordering aid, not a probability: the data has no churn history to fit weights to, and only a handful of clients carry real risk signals. |
| Small UI | A FastAPI service (`api.py`, four endpoints) and a Next.js page in `ui/` that calls it. Run a briefing, click any citation to see the evidence behind it, see the trace, browse the portfolio. The API is a thin layer over the same `run()` function; it loads the data once and runs the pipeline in a worker thread. It is a local, single-user service: no authentication, no job queue for runs of up to a minute, no rate limiting. |
| LLM-as-judge scoring | Not done. I preferred to spend the time on the verifier; a judge model would rate usefulness, which is the part my automatic checks do not cover, so it is the first thing in "next". |

## Known limitations

- **The verifier checks figures, not meaning.** It proves that a figure exists in
  the cited fact with the right sign. What it does not prove, each confirmed by an
  independent review with crafted lines:
  - that the figure is attached to the right subject or unit ("752,000 active
    users" passes next to a contract worth EUR 752,000, and a figure for one
    product passes in a sentence about another);
  - identifiers in prose ("ticket T-9999" next to a valid citation);
  - number words ("halved", "four of five");
  - any sentence without figures. One sample briefing from an earlier run said a
    notice period was "not in the data" because the tool did not state it for an
    expired contract; the tool now states it, but the class of error remains.
  The Verification section of each briefing says this in one sentence and counts
  the lines that were not checked.
- **One repair attempt.** Some briefings still go out with a flagged line. That is
  the intended behaviour, and the exit code reports it, but it is not zero.
- **Note handling is keyword based.** Statements are quoted verbatim and sorted
  into topics by a small word list; the claim check only compares a direction for a
  product the sentence names.
- **Thresholds are judgement calls** (15% year-on-year for a signal, 50%
  utilisation, peer groups of three). They are named constants, not tuned.
- **No notice records.** The data does not say whether notice was given, so an
  auto-renewing contract past its notice date is described as "would roll over
  unless notice was given".
- **Synthetic data only**, 25 clients. The evaluation cases were chosen by me after
  reading the data, so they test what I knew to look for.
- **Name matching** has no typo tolerance.
- Latency was 13 to 28 seconds per briefing in the committed runs, almost all of it
  the model writing; a repair adds one more call.
- **Length.** The prompt asks for about 400 words; with the code-written
  Verification and gaps sections the files are 500 to 700 words, more than one page
  for a client with many gaps.
- **The rep's context does not change the plan.** It reaches the writer only; the
  tools that run depend on the trigger alone.

## What I would do next for production

1. A labelled evaluation set owned by sales operations, run on every prompt or
   model change, with a rep rating usefulness, which no automatic check covers.
2. Tie each figure to its subject: have the writer emit structured claims
   (fact ID plus sentence) so the verifier can check the pairing, not only the number.
3. Put the API behind authentication, move the runs of up to a minute to a job
   queue with status polling, and add rate limits. Read from the warehouse through reviewed SQL views instead of a file, with data
   freshness in the header and row-level access by account owner.
4. Tracing and cost per briefing, an audit log of what was sent to the model, and
   a data-processing review for meeting notes, which contain personal data.
5. Feedback from reps on each briefing, fed back into the trigger configuration.
6. Notice and renewal events from the contract system, which the briefing most
   needs and the data lacks.

## How I built it

**Time.** Timed build on Wednesday 18 November 2026, start 08:59, end RESULT_END.
Before the build, I read the brief and the data pack and wrote
myself a data survey and a schema diagram. So
the design decisions on duplicates, missing months and the seasonal comparison were
made before the coding has started; all code, prompts, tests and this README were
written inside the timed session.

**Tool.** Claude Code, with the instructions in `CLAUDE.md`. I set the architecture
and the rules (numbers from code, fixed sequence, triggers as configuration, flag
instead of delete, what counts as "in force", how to compare seasons); the
assistant wrote the code against them.

**How the work was split.**
1. I had the loader and the shared `Fact` format written first, alone, because
   everything else depends on that contract.
2. Four sub-agents then worked in parallel, each owning its files and nothing
   else: contracts and client resolution; usage and data quality; support, notes
   and white-space; the verifier. Each had to write tests with exact values checked
   against the data. Meanwhile the main session wrote the pipeline, prompts and
   command.
3. Integration check: all 25 clients with all 4 triggers, without a model, through
   the verifier. Zero flags was the bar before any model call.
4. A separate reviewer agent, with no part in the build, recomputed figures from
   the database, attacked the verifier with deliberately wrong lines and ran the
   sample requests. It was told to report only, not to edit.
5. Three agents fixed its findings in parallel, again by file ownership.
6. With the must-haves evaluated, two more agents built the stretch goals in
   parallel against a JSON contract I wrote first: one the trace, parallel tools
   and portfolio in Python, one the web UI in its own folder. The UI first ran
   the command as a child process; I had that replaced by a proper HTTP API,
   since nobody would deploy the first version.

**What worked.** A written data contract before parallel work: four agents
produced code that fitted together at the first attempt. Exact-value tests against
known rows. The model-free sweep as a gate. An independent reviewer: my own tests
all passed while the verifier still accepted a flipped sign.

**What I had to correct.**
- The first verifier accepted "+28.0%" for a fact saying -28.0%, let a row citation
  lend a line every figure computed from that row, and treated figures typed by
  the rep as evidence. All three were found by the reviewer, not by tests.
- Auto-renewing contracts past their notice date were described as ending, which
  would have sent a rep into an emergency that does not exist.
- Open tickets were tagged as "reported" as a whole, so a ticket's age was flagged
  as an unverified claim. Found in the first evaluation run.
- My evaluation's own check was wrong twice (it demanded a row ID where the
  briefing cited the calculation built on it, and it did not know citable gaps).
- Python rounds 1.25 to 1.2; figures now round half up.
- My first time estimate for the evaluation loop was too low; the model's drafts
  needed the repair step in about half the cases, mostly for rewriting units
  ("44.8 million" for a figure whose unit is "impressions (millions)") or for
  citing the wrong one of two facts.

The assistant did not choose the design, and paid model runs happened only on my
instruction.

## Repository

```
CLAUDE.md               instructions the coding assistant worked under
src/client_intel/
  db.py                 typed, de-duplicated load
  evidence.py           Fact / Gap / ToolResult, figure formatting
  tools/                clients, contracts, usage, support, notes, whitespace, claims, quality
  triggers.toml         trigger configuration
  pipeline.py           the sequence
  prompts/              run-time prompts
  llm.py                the only model call
  verify.py             verifier and flag policy
  trace.py              step timing and cost
  portfolio.py          ranking of all clients
  cli.py
  api.py                the same pipeline over HTTP (FastAPI)
ui/                     optional Next.js page that calls the API
eval/                   cases, runner, reports
outputs/                sample briefings and evidence from the evaluation
data/starter_pack/      the provided data, unchanged
tests/
```

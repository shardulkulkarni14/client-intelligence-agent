# Client intelligence agent

One command turns a client and a trigger into a one-page briefing for the account
manager, plus an evidence file that backs every figure in it.

```bash
uv sync
cp .env.example .env          # then put your Anthropic API key in .env
uv run client-intel --client "Halden Bet" --trigger renewal
```

Output goes to `runs/<client id>_<trigger>/briefing.md` and `evidence.json`, and the
briefing is printed.

| Option | Meaning |
|---|---|
| `--client` | name or ID: `"Halden Bet"`, `C001`, `"Brenmoor League"`. An ambiguous name stops with the candidates. |
| `--trigger` | `renewal`, `meeting_prep`, `upsell`, `at_risk` |
| `--context "..."` | free text from the rep |
| `--no-llm` | facts-only briefing without any model call; needs no key |
| `--out DIR` | output folder (default `runs`) |

Exit code: 0 clean, 1 briefing written with flagged lines, 2 request could not be answered.

```bash
uv run pytest                           # RESULT_TESTS tests, no model calls
uv run python eval/run_eval.py          # the evaluation, with the model
uv run python eval/run_eval.py --no-llm # same cases on tool output only, free
```

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). The model is set with
`CLIENT_INTEL_MODEL` (default `claude-haiku-5-5`).

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
| Verify | code, `verify.py` | Every number on a line must be in a fact cited on that line; signs and directions must agree; unknown citations fail. |
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

## Evaluation

`eval/cases.json` holds RESULT_CASES cases over RESULT_CLIENTS clients and all four triggers; four
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

RESULT_BLOCK

Sample briefings and evidence files from this run are in `outputs/`.

Separately, the test suite runs all 25 clients with all 4 triggers without a model
and requires zero verifier flags, which proves that the tools' own sentences are
traceable.

## Known limitations

- **The verifier checks figures, not meaning.** It proves that a figure exists in
  the cited fact with the right sign. It does not prove the figure is attached to
  the right subject within that fact, it does not check number words ("halved"),
  and a sentence without figures is not checked at all; the Verification section
  counts those lines.
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
- Latency is 30 to 60 seconds per briefing, mostly the model writing.

## What I would do next for production

1. A labelled evaluation set owned by sales operations, run on every prompt or
   model change, with a rep rating usefulness, which no automatic check covers.
2. Tie each figure to its subject: have the writer emit structured claims
   (fact ID plus sentence) so the verifier can check the pairing, not only the number.
3. Read from the warehouse through reviewed SQL views instead of a file, with data
   freshness in the header and row-level access by account owner.
4. Tracing and cost per briefing, an audit log of what was sent to the model, and
   a data-processing review for meeting notes, which contain personal data.
5. Feedback from reps on each briefing, fed back into the trigger configuration.
6. Notice and renewal events from the contract system, which the briefing most
   needs and the data lacks.

## How I built it

RESULT_HOWBUILT

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
  cli.py
eval/                   cases, runner, reports
outputs/                sample briefings and evidence from the evaluation
data/starter_pack/      the provided data, unchanged
tests/
```

# Client briefing: Brenmoor Football League (C003), at_risk

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
Yes, the account is at risk, mainly on renewal and streaming. Contract K-0005 ends on 2026-12-31 and does not renew automatically, and the only signed contract on file is K-0005 [contracts:K-0005] [gap:no_previous_contract#1]. Confidence is moderate: the usage and contract facts are measured and the data is clean, but the reported renewal agreement conflicts with the measured STREAM decline.

## Warning signs
- Renewal is not signed. K-0005 ends 2026-12-31 unless a new contract is signed, and the notice deadline of 2026-10-02 has passed [contracts:K-0005] [calc:contract_status#2]. The renewal opportunity O-0003 is at Proposal stage, with an amount of EUR 258,500 and an expected close of 2026-12-15 [opp:O-0003].
- The CRM next step reads "Awaiting client board approval" [opp:O-0003]. The last meeting was 44 days before 2026-11-01 [calc:meeting_notes#1].
- STREAM usage fell: 1,292 streamed hours in Aug-Oct 2026 versus 1,669 in Aug-Oct 2025, a change of -22.6% [calc:usage_trend#24].
- The most recent ticket, T-0258 (opened 2026-08-28), asks to pause streams for cup matches moved to a free-to-air partner [ticket:T-0258].

## Signs of health
- Three of four products grew year on year: INTEGRITY +3.0% [calc:usage_trend#10], FAN_INSIGHTS +8.0% [calc:usage_trend#3], STATS_ARCHIVE +6.3% [calc:usage_trend#17].
- No open tickets at 2026-11-01, and 1 ticket opened in the last 90 days versus 4 in the previous 90 days [calc:support_summary#13] [calc:support_summary#12].
- Average CSAT is 4.1 out of 5 over the last 12 months [calc:support_summary#5].
- Data confidence is high, so these figures can be relied on [calc:data_quality#1].

## What we do not know
- Whether the board will approve. The note says the renewal was "basically agreed" at around +10%, pending the board. This is reported by Tomas Ferreira, not measured [note:N-006]. The opportunity is +10.0% versus the current annual value of EUR 235,000 [calc:opportunities#1].
- Why STREAM is falling. The commercial director reportedly said usage is "up massively" [note:N-006]. This conflicts with the measured -22.6% [calc:claim_check#1] [gap:source_conflict#1]. STREAM did rise +24.0% over the previous three months, but that comparison is not seasonally adjusted [calc:usage_trend#25].
- Whether the free-to-air move is permanent or how many matches it covers. The ticket subject is the only evidence [ticket:T-0258].

## Suggested next steps
- Call the board-facing contact to confirm where the renewal stands before the expected close of 2026-12-15 [opp:O-0003].
- Send the renewal paperwork, which the note assigns to Tomas Ferreira, and confirm it has gone out [note:N-006] [client:C003].
- Ask the client directly about the free-to-air move and its effect on STREAM volume [ticket:T-0258] [calc:usage_trend#24].
- Do not repeat the "up massively" claim in any proposal until it is checked against the measured -22.6% [calc:usage_trend#24] [calc:claim_check#1].

## Verification

All 31 numbers and 30 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0005 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0005]
- Note N-006 and the usage data disagree about STREAM; the briefing uses the measured figure. [gap:source_conflict#1][note:N-006]

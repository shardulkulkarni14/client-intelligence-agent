# Client briefing: Brenmoor Football League (C003), at_risk

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
Yes, the account is at real risk, mainly through the renewal. Contract K-0005 ends on 2026-12-31 and does not renew automatically [contracts:K-0005] [calc:contract_status#1], and the renewal O-0003 is still at Proposal [opp:O-0003]. Confidence is moderate: the measured data is reliable [calc:data_quality#1], but the renewal is unsigned and the most positive account of streaming conflicts with the measured figures [calc:claim_check#1].

## Warning signs
- The notice deadline for K-0005 was 2026-10-02 and passed 30 days before 2026-11-01 [calc:contract_status#2]. Without a signed renewal, the contract ends 60 days after 2026-11-01 [calc:contract_status#1].
- Renewal O-0003 is EUR 258,500, +10.0% on EUR 235,000, with expected close 2026-12-15 [opp:O-0003] [calc:opportunities#1]. The CRM reads "Awaiting client board approval" (reported) [opp:O-0003]. A note reports the renewal as "basically agreed" at around +10%, pending the board (reported) [note:N-006].
- STREAM, the largest fee at EUR 110,000 a year [contracts:K-0005], fell -22.6% year on year: 1,292 streamed hours in Aug-Oct 2026 against 1,669 in Aug-Oct 2025 [calc:usage_trend#21]. A note reports the commercial director saying streaming is "up massively" (reported) [note:N-006], which the measured figures contradict [calc:claim_check#1].
- Support: 3 P1/P2 tickets in the last 12 months, and Integration is the top category with 4 [calc:support_summary#4] [calc:support_summary#3].

## Signs of health
- Other modules are up year on year: Integrity +3.0%, Stats Archive +6.2%, Fan Insights +8.0% [calc:usage_trend#9] [calc:usage_trend#15] [calc:usage_trend#3].
- No module exceeded its included volume in Aug-Oct 2026 (0 of 3 months for each) [calc:usage_trend#6] [calc:usage_trend#24].
- Ticket volume is falling: 1 opened in the last 90 days versus 4 in the previous 90 days, and no tickets are open [calc:support_summary#12] [calc:support_summary#13].

## What we do not know
- Whether the board will approve the renewal, and on what terms.
- Why STREAM fell. The data gives no cause, and the reported growth is unverified.
- Whether the decline will continue. Usage is not seasonally adjusted [calc:usage_trend#22].
- The change in annual value at the last renewal. K-0005 is the only signed contract on file.
- What the passed notice deadline means for the renewal terms. The data does not say.

## Suggested next steps
- Before the +10% goes to the board, check the "up massively" claim with the commercial director and reconcile it with the -22.6% STREAM decline [note:N-006] [calc:usage_trend#21]. Owner: Tomas Ferreira.
- Confirm the board date for O-0003 so the renewal is signed before the 2026-12-31 end date [opp:O-0003] [contracts:K-0005].
- Ask what drove the STREAM decline and whether streaming volume will recover, given it is EUR 110,000 of the annual fee [contracts:K-0005].
- Review the 4 Integration tickets with the client's technical contact before the renewal call [calc:support_summary#3].
- Record the conflict between N-006 and the measured data in the CRM, so the renewal forecast does not rely on the "up massively" claim [calc:claim_check#1].

## Verification

All 35 numbers and 32 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0005 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [contracts:K-0005]
- Note N-006 and the usage data disagree about STREAM; the briefing uses the measured figure. [note:N-006]

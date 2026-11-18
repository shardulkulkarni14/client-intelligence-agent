# Client briefing: Brenmoor Football League (C003), at_risk

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The account is at real risk of shrinking, and the timing is tight. Contract K-0005 ends on 2026-12-31, 60 days after 2026-11-01 [contracts:K-0005] [calc:contract_status#1], and no renewal is signed. Confidence is medium: the contract and usage figures are measured [calc:data_quality#1], but the "basically agreed" renewal rests on a reported claim that the measured STREAM data contradicts.

## Warning signs
- The notice deadline of 2026-10-02 passed 30 days before 2026-11-01, and K-0005 does not renew automatically [calc:contract_status#2] [contracts:K-0005].
- STREAM usage fell: 1,292 streamed hours in Aug-Oct 2026 versus 1,669 in Aug-Oct 2025, a change of -22.6% year on year [calc:usage_trend#24]. STREAM is a EUR 110,000 line in K-0005 [contracts:K-0005].
- Ticket T-0258 (2026-08-28) asks to "pause streams for cup matches moved to free-to-air partner" [ticket:T-0258].
- Note N-006 (written by Tomas Ferreira, 2026-09-18) reports "up massively" streaming usage, but this conflicts with the measured -22.6% [note:N-006] [calc:claim_check#1].

## Signs of health
- No open tickets at 2026-11-01, and ticket volume is down: 1 opened in the last 90 days versus 4 in the previous 90 days [calc:support_summary#13] [calc:support_summary#12].
- Usage is up year on year on three other products: FAN_INSIGHTS +8.0% [calc:usage_trend#3], INTEGRITY +3.0% [calc:usage_trend#10], STATS_ARCHIVE +6.3% [calc:usage_trend#17].
- Renewal opportunity O-0003 is open at EUR 258,500, +10.0% on the K-0005 annual value [opp:O-0003] [calc:opportunities#1].
- Average CSAT is 4.1 out of 5 from 7 rated tickets over 12 months [calc:support_summary#5].

## What we do not know
- Whether the league board will approve the renewal. The CRM next step reads "Awaiting client board approval" [opp:O-0003], and N-006 records the renewal as "basically agreed" pending the board [note:N-006].
- Why STREAM fell. Ticket T-0258 points to cup matches moved to a free-to-air partner, but the data does not confirm this as the cause.
- How the last renewal changed the annual value. K-0005 is the only signed contract on file [gap:no_previous_contract#1].

## Suggested next steps
- Send the renewal paperwork recorded as your action in N-006 [note:N-006], and push for a board decision before the expected close of 2026-12-15 [opp:O-0003].
- Before the board meets, confirm with the league which matches moved to the free-to-air partner, to explain the -22.6% STREAM decline [calc:usage_trend#24] [ticket:T-0258].
- Size the STREAM volume in the renewal against actual use: 435 streamed hours in Oct 2026 against 600 included [calc:usage_trend#23].
- Correct the CRM record so the "basically agreed" claim is marked as unverified against the STREAM data [note:N-006] [calc:claim_check#1].

## Verification

All 34 numbers and 28 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- Contract K-0005 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0005]
- Note N-006 and the usage data disagree about STREAM; the briefing uses the measured figure. [gap:source_conflict#1][note:N-006]

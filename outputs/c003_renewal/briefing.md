# Client briefing: Brenmoor Football League (C003), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is at risk of not closing in time, though the value looks achievable. The notice deadline of 2026-10-02 has passed, and K-0005 ends on 2026-12-31 unless a new contract is signed [calc:contract_status#2] [contracts:K-0005]. A renewal opportunity at EUR 258,500 is at Proposal stage, but the +10% is only reported verbally and is still awaiting board approval, so confidence is moderate [opp:O-0003] [note:N-006].

## Contract and renewal position
- K-0005 runs 2024-01-01 to 2026-12-31 at an annual value of EUR 235,000 and does not renew automatically [contracts:K-0005].
- The notice deadline was 2026-10-02 and passed 30 days before 2026-11-01 [calc:contract_status#2]. The data does not say what this means for the client's options.
- Renewal opportunity O-0003 is at Proposal, EUR 258,500, +10.0% on the current value, with expected close 2026-12-15 [opp:O-0003] [calc:opportunities#1].
- The CRM next step reads "Awaiting client board approval" [opp:O-0003]. Tomas Ferreira's 2026-09-18 note says the renewal is "basically agreed" at around +10%, pending the board [note:N-006].

## Usage against what they pay for
- Most products are within their included volumes: FAN_INSIGHTS was at 72.0% in Oct 2026 [calc:usage_trend#2], INTEGRITY at 87.3% [calc:usage_trend#9], and STATS_ARCHIVE at 83.0% [calc:usage_trend#16].
- Year-on-year volume is up for three products: FAN_INSIGHTS +8.0% [calc:usage_trend#3], INTEGRITY +3.0% [calc:usage_trend#10], STATS_ARCHIVE +6.3% [calc:usage_trend#17].
- STREAM is the exception: 1,292 streamed hours in Aug-Oct 2026 against 1,669 a year earlier, a change of -22.6% [calc:usage_trend#24].

## Risks to the renewal
- STREAM usage is falling. A client ticket asked to pause streams for cup matches moved to a free-to-air partner [ticket:T-0258]. The data does not confirm whether this caused the decline.
- The reported claim that streaming usage is "up massively" [note:N-006] conflicts with the measured -22.6% [calc:claim_check#1]. This briefing uses the measured figure [gap:source_conflict#1].
- Support is not a blocker: no open tickets [calc:support_summary#13] and average CSAT of 4.1 from 7 rated tickets [calc:support_summary#5].

## Room to grow
- Match Visualisation Widgets (WIDGETS) is not held, with an indicative price of EUR 30,000 per year, and is often bought with held STREAM and STATS_ARCHIVE [product:WIDGETS].
- Pre-match Odds Feed (ODDS_PRE) is not held, at an indicative EUR 45,000 per year, and is often bought with held INTEGRITY [product:ODDS_PRE].
- In-play Odds Feed (ODDS_LIVE) is blocked until the client takes Live Match Data Feed (LIVE_DATA), which it does not hold [product:ODDS_LIVE].

## Suggested next steps
- Ask Tomas Ferreira whether the renewal paperwork has gone out, as the 2026-09-18 note committed [note:N-006] [client:C003].
- Get the board approval date and written confirmation of EUR 258,500 before 2026-12-15 [opp:O-0003].
- Raise the STREAM decline and the free-to-air pause request with the client before signing [calc:usage_trend#24] [ticket:T-0258].
- Use measured usage, not the reported "up massively" claim, in the renewal discussion [calc:claim_check#1].

## Verification

All 34 numbers and 32 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0005 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0005]
- Note N-006 and the usage data disagree about STREAM; the briefing uses the measured figure. [gap:source_conflict#1][note:N-006]
- Peer holdings for C007 are taken from an expired contract because none is in force. [gap:peer_holding_based_on_expired_contract#1][client:C007]

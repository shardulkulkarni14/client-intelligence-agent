# Client briefing: Brenmoor Football League (C003), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not secured yet. Contract K-0005 ends on 2026-12-31, 60 days after the data date, and does not renew automatically [calc:contract_status#1][contracts:K-0005]. The renewal opportunity O-0003 is at EUR 258,500, which is +10.0% on the current annual value [calc:opportunities#1], and the CRM says it is awaiting client board approval [opp:O-0003]. Confidence is moderate: the data is high quality [calc:data_quality#1], but the notice deadline has passed [calc:contract_status#2] and the client's account of streaming conflicts with measured usage [calc:claim_check#1].

## Contract and renewal position
- K-0005 runs 2024-01-01 to 2026-12-31 at an annual value of EUR 235,000 [contracts:K-0005].
- The notice deadline was 2026-10-02 and passed 30 days before 2026-11-01 [calc:contract_status#2]. The facts do not say what a missed notice date changes contractually.
- O-0003 is at Proposal with an expected close of 2026-12-15 [opp:O-0003]. The change from the last renewal is not known [gap:no_previous_contract#1].
- Reported in note N-006: renewal "basically agreed" at around +10%, pending their board [note:N-006]. This is not signed.

## Usage against what they pay for
- Integrity: 785 matches monitored in Aug-Oct 2026, +3.0% year on year, at 87.2% average utilisation [calc:usage_trend#10][calc:usage_trend#12].
- Live Streaming: 1,292 streamed hours in Aug-Oct 2026, -22.6% year on year [calc:usage_trend#24]. October utilisation was 72.5% [calc:usage_trend#23].
- Fan Insights: 18 active dashboard users in Oct 2026 against 25 included, 72.0% [calc:usage_trend#2].
- Historical Stats: 166 queries (thousands) in Oct 2026 against 200 included, 83.0% [calc:usage_trend#16].

## Risks to the renewal
- Reported: streaming usage is "up massively" [note:N-006]. Measured streaming use fell year on year [calc:usage_trend#24], which is a direct conflict [calc:claim_check#1][gap:source_conflict#1].
- Ticket T-0258 asks to "pause streams for cup matches moved to free-to-air partner" (subject as written by the client) [ticket:T-0258]. This could reduce streaming volume further.
- Support: 3 P1/P2 tickets in the last 12 months [calc:support_summary#4], with average CSAT of 4.1 out of 5 [calc:support_summary#5]. Ticket volume is down, with no open tickets [calc:support_summary#12][calc:support_summary#13].

## Room to grow
- The client holds 4 of 8 catalogue products [calc:whitespace#1].
- Match Visualisation Widgets is not held. It is often bought with held FAN_INSIGHTS, STATS_ARCHIVE and STREAM, at an indicative EUR 30,000 per year, but 0 of 5 segment peers hold it [product:WIDGETS][calc:whitespace#2].
- In-play Odds Feed is blocked, because it requires Live Match Data Feed, which the client does not hold [product:ODDS_LIVE].

## Suggested next steps
- Ask Tomas Ferreira to confirm the notice position and the terms that apply to K-0005 after 2026-12-31 [contracts:K-0005][calc:contract_status#2].
- Chase board approval for O-0003 at EUR 258,500 ahead of the expected close of 2026-12-15 [opp:O-0003].
- Check the streaming claim with the commercial director before the renewal paperwork goes out, and cover the cup-match move raised in T-0258 [calc:claim_check#1][ticket:T-0258].
- Once the renewal is agreed, raise Widgets as an add-on at an indicative EUR 30,000 per year [product:WIDGETS].

## Verification

All 41 numbers and 37 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0005 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0005]
- Note N-006 and the usage data disagree about STREAM; the briefing uses the measured figure. [gap:source_conflict#1][note:N-006]
- Peer holdings for C007 are taken from an expired contract because none is in force. [gap:peer_holding_based_on_expired_contract#1][client:C007]

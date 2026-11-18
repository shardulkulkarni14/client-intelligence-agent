# Client briefing: Halden Bet (C001), renewal

_Data as of 2026-11-01. Account owner: Maya Lindgren._

## Bottom line
This renewal is not on track. The notice deadline is 2026-12-02 [calc:contract_status#2], and the open renewal opportunity is EUR 541,500, which is -28.0% against the current annual value of EUR 752,000 [opp:O-0001] [calc:opportunities#1]. The contract facts are high confidence [calc:data_quality#1], but the reduced-scope pricing that drives the gap is reported, not measured [opp:O-0001].

## Contract and renewal position
- K-0002 is in force and ends 2027-01-31, 91 days after 2026-11-01 [calc:contract_status#1].
- It renews automatically for the same term unless notice is given, with a notice period of 60 days [contracts:K-0002].
- The annual value is EUR 752,000, up +8.7% on EUR 692,000 for K-0001 [calc:contract_status#3].
- The opportunity O-0001 is at Negotiation, with an expected close of 2027-01-15, which is after the notice deadline [opp:O-0001] [calc:contract_status#2].

## Usage against what they pay for
- Usage is falling: LIVE_DATA is -36.3% year on year for Aug-Oct 2026 [calc:usage_trend#3], and ODDS_LIVE is -40.0% [calc:usage_trend#10].
- ODDS_LIVE used 51.6% of its included volume in Oct 2026 [calc:usage_trend#9].
- ODDS_PRE is close to its included volume: 89.8% used in Oct 2026 [calc:usage_trend#16], and up +24.2% on the previous three months [calc:usage_trend#18].

## Risks to the renewal
- A competitor trial is reported: the head of trading is "trialling another in-play odds supplier" for two leagues [note:N-003].
- Two P1/P2 tickets are open: T-0284, P1 latency on ODDS_LIVE, open 11 days [ticket:T-0284]; and T-0279, P2 missing events on LIVE_DATA, open 20 days [ticket:T-0279].
- Satisfaction is low: average CSAT is 1.3 out of 5 over the last 90 days, from 4 rated tickets [calc:support_summary#10].
- Budget pressure is reported from the client's finance team [note:N-003].

## Room to grow
- Match Visualisation Widgets (WIDGETS) is not held; it is often bought with LIVE_DATA and STREAM, which the client holds, at an indicative EUR 30,000 per year [product:WIDGETS].
- Integrity Monitoring (INTEGRITY) is not held; it is often bought with ODDS_PRE, at an indicative EUR 25,000 per year [product:INTEGRITY].
- The client was "still positive about the live data feed and pre-match odds" [note:N-003].

## Suggested next steps
- Before 2026-12-02, decide with the client whether to renew on the current terms or give notice, since renewal is automatic [contracts:K-0002] [calc:contract_status#2].
- Build the reduced in-play scope pricing that procurement asked for [note:N-003] and set it against the EUR 541,500 opportunity [opp:O-0001].
- Close the open P1 and P2 tickets, T-0284 and T-0279, before the pricing discussion [ticket:T-0284] [ticket:T-0279].
- Prepare the renewal options that Maya committed to before the notice date [note:N-003].

## Verification

All 30 numbers and 30 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

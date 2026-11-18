# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line
Yes, the account is at risk of shrinking, and the risk is concentrated in the in-play products. The measured signals (falling in-play usage, two open P1/P2 tickets, low CSAT, and a renewal opportunity priced below the current contract) support this. There is no measured sign of leaving, and the competitor trial and the phone-call mood rest only on reports, so confidence is moderate on shrinkage and low on departure.

## Warning signs
- Renewal: contract K-0002 renews automatically unless notice is given, and the notice deadline is 2026-12-02, 31 days after 2026-11-01 [calc:contract_status#2] [contracts:K-0002].
- Renewal opportunity O-0001 is at EUR 541,500, -28.0% versus the EUR 752,000 contract in force [calc:opportunities#1]. The CRM next step reads "Client asked for pricing on reduced in-play scope" (reported) [opp:O-0001].
- Open tickets: 2 open, both P1/P2 [calc:support_summary#13]. T-0284 (P1, latency, ODDS_LIVE) has been open 11 days [ticket:T-0284]. T-0279 (P2, missing events, LIVE_DATA) has been open 20 days [ticket:T-0279].
- Measured usage is down year on year: ODDS_LIVE -40.0% [calc:usage_trend#10] and LIVE_DATA -36.3% [calc:usage_trend#3].
- Satisfaction is low: CSAT 1.3 out of 5 from 4 rated tickets in the last 90 days [calc:support_summary#10]. Ticket volume is up, with 7 opened in the last 90 days versus 2 in the previous 90 days [calc:support_summary#12].
- A competitor trial is reported: the head of trading said they are trialling another in-play odds supplier "for two leagues" since the summer (reported, note N-003) [note:N-003].
- The rep reports that the head of trading sounded unhappy on a recent phone call. This is the rep's impression, not a recorded fact.

## Signs of health
- Pre-match odds are growing: ODDS_PRE usage is +24.2% versus the previous three months [calc:usage_trend#18], and utilisation was 89.8% in Oct 2026 [calc:usage_trend#16].
- The client is still positive about the live data feed and pre-match odds (reported) [note:N-003].
- The current contract is worth +8.7% more than K-0001 [calc:contract_status#3]. The client is Strategic tier and has been a customer since 2021-02-01 [client:C001].
- Data confidence is high, so the figures above can be relied on [calc:data_quality#1].

## What we do not know
- Whether the client will give notice, or whether the reduced in-play scope will be the final renewal shape. The facts do not say.
- Whether the competitor trial is real and how far it has gone. It is reported only, and no usage data shows a shift to another supplier.
- Why in-play usage has fallen. The facts record the drop but not its cause.
- Whether the service credits requested in June were agreed (N-002 records the request only) [note:N-002].

## Suggested next steps
- Confirm with Maya Lindgren, the account owner, whether the renewal will go to notice before 2026-12-02 [calc:contract_status#2].
- Get written status on T-0284 and T-0279 before the renewal talk, since both are open and P1/P2 [calc:support_summary#13].
- Prepare a reduced in-play scope option, since procurement has asked for it (reported) [note:N-003], and price it against the O-0001 amount of EUR 541,500 [opp:O-0001].
- Ask the head of trading directly about the competitor trial and the latency complaints, and record the answers in the CRM.

## Verification

All 26 numbers and 23 citations were checked against the evidence.

6 lines carry no figure and no citation; they are interpretation and were not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

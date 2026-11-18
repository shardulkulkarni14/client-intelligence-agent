# Client briefing: Halden Bet (C001), renewal

_Data as of 2026-11-01. Account owner: Maya Lindgren._

## Bottom line
The renewal is at risk. Contract K-0002 (EUR 752,000 a year) renews automatically on 2027-01-31 unless notice is given by 2026-12-02 [contracts:K-0002] [calc:contract_status#2]. The open renewal opportunity is at EUR 541,500, 28.0% below the current value [opp:O-0001] [calc:opportunities#1]. The data is high confidence [calc:data_quality#1], but the reduced-scope request is reported rather than measured, so the final value is uncertain.

## Contract and renewal position
- K-0002 is in force and ends 2027-01-31, 91 days after 2026-11-01 [contracts:K-0002] [calc:contract_status#1].
- The notice deadline is 2026-12-02, 31 days after 2026-11-01 [calc:contract_status#2].
- The annual value rose +8.7% from EUR 692,000 on K-0001 [calc:contract_status#3].
- Opportunity O-0001 is at Negotiation, with an expected close of 2027-01-15, which is after the notice deadline [opp:O-0001] [calc:contract_status#2].
- Reported CRM next step: "Client asked for pricing on reduced in-play scope" [opp:O-0001].

## Risks to the renewal
- Reported: the head of trading is trialling another in-play odds supplier "for two leagues" [note:N-003].
- Reported: budget pressure from their finance team [note:N-003].
- Support volume is up: 7 tickets in the last 90 days versus 2 in the previous 90 days [calc:support_summary#12].
- CSAT over the last 90 days is 1.3 out of 5, from 4 rated tickets [calc:support_summary#10].
- Open P1 T-0284 (in-play latency, ODDS_LIVE) has been open 11 days, and open P2 T-0279 (data accuracy, LIVE_DATA) has been open 20 days [ticket:T-0284] [ticket:T-0279].
- Conflict: the 2026-10-07 note says the client is "still positive about the live data feed" [note:N-003], but live data usage is down -36.3% year on year [calc:usage_trend#3].

## Usage against what they pay for
- LIVE_DATA used 55.3% of its 8,000 included in Oct 2026 [calc:usage_trend#2].
- ODDS_LIVE is down -40.0% year on year and used 51.6% of its 1,920 included in Oct 2026 [calc:usage_trend#10] [calc:usage_trend#9].
- ODDS_LIVE exceeded its included volume in 5 of the last 12 months [calc:usage_trend#14].
- ODDS_PRE used 89.8% of its 1,280 included in Oct 2026 and is up +24.2% on the previous three months [calc:usage_trend#16] [calc:usage_trend#18].
- STREAM used 56.4% of its 960 included in Oct 2026 [calc:usage_trend#23].

## Room to grow
- Not held: Match Visualisation Widgets, indicative EUR 30,000 per year, often bought with LIVE_DATA and STREAM [product:WIDGETS].
- Not held: Integrity Monitoring, indicative EUR 25,000 per year, often bought with ODDS_PRE [product:INTEGRITY].
- Reported: interest in more streaming for lower leagues, "nothing concrete" [note:N-001].

## Suggested next steps
- Before 2026-12-02, agree the renewal position with the client, since the auto-renewal applies after that date [calc:contract_status#2].
- Price a reduced in-play scope against the EUR 541,500 opportunity and the EUR 752,000 current value [opp:O-0001] [contracts:K-0002].
- Resolve P1 T-0284 and P2 T-0279 before the pricing discussion [ticket:T-0284] [ticket:T-0279].
- Confirm which leagues the competing trial covers, since this is reported and not verified [note:N-003].
- Deliver the renewal options Maya committed to before the notice date, as recorded in the note [note:N-003].

## Verification

All 47 numbers and 37 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

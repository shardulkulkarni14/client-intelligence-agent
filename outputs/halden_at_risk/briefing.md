# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line
Yes, the account is at elevated risk of shrinking at renewal. The notice deadline is 2026-12-02, which is 31 days after 2026-11-01 [calc:contract_status#2]. Measured service and usage signals support this strongly. The competitor trial and the budget pressure are reported in CRM notes, not measured, so the direction is well supported but the detail is not confirmed.

## Warning signs
- **Renewal:** Contract K-0002 renews automatically for the same term unless notice is given, with a 60-day notice period [contracts:K-0002]. The open renewal opportunity O-0001 is at Negotiation for EUR 541,500, which is -28.0% against the EUR 752,000 annual value [opp:O-0001][calc:opportunities#1].
- **Service:** Two tickets are open, both P1/P2 [calc:support_summary#13]. T-0284 (P1, latency) has been open 11 days [ticket:T-0284], and T-0279 (P2, data accuracy) has been open 20 days [ticket:T-0279]. Average CSAT over the last 90 days is 1.3 out of 5, from 4 rated tickets [calc:support_summary#10]. Tickets rose to 7 from 2 in the previous 90 days [calc:support_summary#12].
- **Usage:** ODDS_LIVE usage is -40.0% year on year for Aug-Oct [calc:usage_trend#10]. LIVE_DATA is -36.3% [calc:usage_trend#3].
- **Reported competitor and budget claims:** In note N-003 (written by Maya Lindgren), the head of trading "mentioned they are trialling another in-play odds supplier 'for two leagues' since the summer." The note also reports "budget pressure from their finance team" [note:N-003].

## Signs of health
- **Pre-match odds are growing:** ODDS_PRE usage is +24.2% against the previous three months and utilisation was 89.8% in Oct 2026 [calc:usage_trend#18][calc:usage_trend#16].
- **Streaming is growing:** STREAM usage is +23.2% against the previous three months [calc:usage_trend#25].
- **Reported goodwill:** Note N-003 says the client is "still positive about the live data feed and pre-match odds" [note:N-003]. The annual contract value is +8.7% above the previous contract's EUR 692,000 [calc:contract_status#3].

## What we do not know
- Whether the competitor trial is real, and how far it extends. This rests only on a reported remark in N-003 [note:N-003].
- Whether the client has already given notice, or plans to. The facts do not say [contracts:K-0002].
- What the reduced in-play scope covers, and whether the renewal amount on O-0001 reflects it [opp:O-0001].
- How much the budget pressure is, and whether it is driving the pricing request [note:N-003].
- Whether the head of trading's unhappiness, which the rep reports from a recent call, reflects the client's formal position. It is not recorded in the data.
- Whether the June service credits and incident summary from N-002 were delivered. The facts do not record the outcome [note:N-002].

## Suggested next steps
- **Before 2026-12-02:** Confirm with Maya Lindgren whether notice has been given or is planned [calc:contract_status#2][contracts:K-0002].
- **Resolve open tickets:** Get a written status and recovery date for T-0284 and T-0279 from the support team, since both are P1/P2 and open [ticket:T-0284][ticket:T-0279].
- **Test the competitor claim:** Ask the head of trading directly which in-play scope is being trialled and for how long, then compare with the ODDS_LIVE decline [note:N-003][calc:usage_trend#10].
- **Prepare renewal options:** Build pricing for the reduced in-play scope that the client asked about [opp:O-0001], while keeping the live data feed and pre-match odds that the client still values [note:N-003].

## Verification

All 25 numbers and 30 citations were checked against the evidence.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

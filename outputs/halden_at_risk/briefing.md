# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line

Halden Bet is at real risk of shrinking at renewal, most likely through a reduced in-play scope rather than a full exit. Measured usage is down, support problems are concentrated in in-play services, and the renewal opportunity is priced 28.0% below the current contract [calc:opportunities#1] [calc:usage_trend#10] [calc:support_summary#13] [calc:contract_status#2]. Confidence is moderate: the data is high quality, but the competitor trial and the scope request come from notes, not measurements, and nothing shows the client leaving.

## Warning signs

- **Renewal deadline:** Contract K-0002 renews automatically unless notice is given. The notice deadline is 2026-12-02, 31 days after 2026-11-01 [contracts:K-0002] [calc:contract_status#2].
- **Open escalations:** 2 open tickets, both P1/P2 [calc:support_summary#13]. T-0284 (P1, latency) has been open 11 days [ticket:T-0284]. T-0279 (P2, data accuracy) has been open 20 days [ticket:T-0279].
- **Reported competitor trial and scope cut:** Note N-003 says the head of trading is trialling another in-play odds supplier "for two leagues" and that procurement wants pricing for a reduced in-play scope. The CRM records the same request [note:N-003] [opp:O-0001].
- **Falling in-play usage and poor service ratings:** ODDS_LIVE usage is down 40.0% year on year [calc:usage_trend#10]. CSAT is 1.3 out of 5 over the last 90 days, from 4 rated tickets, and ticket volume rose to 7 from 2 in the prior 90 days [calc:support_summary#10] [calc:support_summary#12].

## Signs of health

- **Pre-match usage is growing:** ODDS_PRE usage is up 24.2% against May-Jul 2026, and October utilisation was 89.8% of included volume [calc:usage_trend#18] [calc:usage_trend#16].
- **Contract value grew:** K-0002 is worth EUR 752,000 a year, up 8.7% from EUR 692,000 on K-0001. The client is Strategic tier and has been a customer since 2021-02-01 [calc:contract_status#3] [client:C001].
- **Reported positive view:** Maya Lindgren's note says the client is "still positive about the live data feed and pre-match odds" [note:N-003].

## What we do not know

- Whether the usage drop is caused by the competitor trial. The data does not link them.
- How large the competitor trial is, or whether it will move beyond "two leagues".
- Whether the rep's impression of the head of trading's tone, from last week's call, reflects the wider client view. It is not recorded in the data.
- Whether the renewal options promised at the 2026-10-07 meeting have been prepared. The last meeting was 25 days before the data date [calc:meeting_notes#1].

## Suggested next steps

- Before 2026-12-02, confirm with Maya Lindgren that renewal options are ready, as promised in N-003 [note:N-003] [calc:contract_status#2].
- Ask the head of trading directly about the in-play supplier trial and the reduced scope, and record the answers in the CRM [note:N-003] [opp:O-0001].
- Get status updates on T-0284 and T-0279 from support, and tell the client when they will be resolved [ticket:T-0284] [ticket:T-0279].
- Price any reduced in-play scope against the current contract before quoting, since the opportunity is already 28.0% below it [calc:opportunities#1].

## Verification

All 26 numbers and 27 citations were checked against the evidence.

3 lines carry no figure and no citation; they are interpretation and were not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

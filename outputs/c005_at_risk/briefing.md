# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The usage and support data do not show the account shrinking or leaving. The real exposure is timing: contract K-0008 ends on 2026-11-30 [calc:contract_status#1] and renews automatically, the notice deadline has already passed, and no renewal opportunity is on file. Confidence is medium, because the renewal intent is unknown and the data has gaps [calc:data_quality#1].

## Warning signs
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and renews automatically for the same term unless notice is given [calc:contract_status#1] [contracts:K-0008].
- The notice deadline was 2026-10-01 and passed 31 days before 2026-11-01. The data holds no record of notice either way [calc:contract_status#2] [calc:contract_status#3].
- The term fell from 24 months on K-0007 to 12 months on K-0008 [calc:contract_status#5].
- No renewal opportunity is recorded [calc:opportunities#1] [gap:no_renewal_opportunity#1].

## Signs of health
- Year on year, usage rose for three services: Live Match Data Feed +6.8% [calc:usage_trend#3], Live Streaming +3.9% [calc:usage_trend#17], Widgets +5.5% [calc:usage_trend#24]. Historical Stats Archive fell -5.9% [calc:usage_trend#10].
- Widgets used 101.8% of included volume in Oct 2026 [calc:usage_trend#23]. The indicative overage is EUR 240, with no billing data to confirm it was charged [calc:usage_trend#29].
- No open tickets at 2026-11-01 [calc:support_summary#13]. Ticket volume is unchanged over 90 days [calc:support_summary#12]. Average CSAT over 12 months is 4.2 out of 5 [calc:support_summary#5].
- A reported positive from Grace Okafor's note: "Widgets performing well on their website." [note:N-010]

## What we do not know
- Whether the client intends to renew, or whether notice was given. The data is silent [calc:contract_status#3].
- The last recorded meeting was 2026-05-20, 165 days before 2026-11-01 [calc:meeting_notes#1].
- Whether the reported missing March usage statement was resolved. Grace's note says she would chase it [note:N-010], but no follow-up is on file.
- Usage for March 2026 is unknown, not zero, for all four services [gap:missing_month#1] [gap:missing_month#2] [gap:missing_month#3] [gap:missing_month#4].

## Suggested next steps
- Before 2026-11-30, ask Grace Okafor whether notice was received and whether the client plans to renew [calc:contract_status#1] [client:C005].
- Open a renewal opportunity in the CRM, since none is recorded [gap:no_renewal_opportunity#1].
- Confirm whether the March usage statement issue was resolved, as reported in the 2026-05-20 note [note:N-010].
- Check billing for the indicative overage before raising it with the client [calc:usage_trend#29].

## Verification

All 27 numbers and 31 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

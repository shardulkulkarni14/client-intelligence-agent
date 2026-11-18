# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The main risk is contract timing, not falling usage. Contract K-0008 ends on 2026-11-30, and its notice deadline of 2026-10-01 has passed with no record of notice either way, so it would roll over for another 12 months unless notice was given [calc:contract_status#1] [calc:contract_status#2] [calc:contract_status#3]. Usage has held up, but the data cannot show whether the client intends to leave. Confidence is medium [calc:data_quality#1].

## Warning signs
- Renewal is close: K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded [calc:contract_status#1] [calc:opportunities#1].
- The notice deadline passed 31 days before 2026-11-01 with no record of notice [calc:contract_status#2] [calc:contract_status#3].
- The term was cut from 24 months on K-0007 to 12 months on K-0008 [calc:contract_status#5].
- A note reports a complaint: "They could not find their March usage statement in the portal; support ticket raised" (reported, Grace Okafor's note) [note:N-010].

## Signs of health
- No open tickets at 2026-11-01 [calc:support_summary#13]. The one P1 outage, T-0194, closed in 4 days with CSAT 5 out of 5 [ticket:T-0194].
- Usage is mixed year on year: LIVE_DATA +6.8% [calc:usage_trend#3], STATS_ARCHIVE -5.9% [calc:usage_trend#10], STREAM +3.9% [calc:usage_trend#17], WIDGETS +5.5% [calc:usage_trend#24].
- WIDGETS reached 101.8% of its included volume in Oct 2026 [calc:usage_trend#23]. The estimated overage is an indicative EUR 240, with no billing data to confirm it was charged [calc:usage_trend#29].
- Annual value is EUR 363,000, up 4.3% on EUR 348,000 for K-0007 [calc:contract_status#4]. A note reports "Widgets performing well on their website" (reported) [note:N-010].

## What we do not know
- Whether notice was sent before 2026-10-01; the data holds no record [calc:contract_status#3].
- The client's renewal intent. Only one meeting note exists, from 2026-05-20, 165 days before 2026-11-01 [calc:meeting_notes#1]. No CRM opportunity is on file [gap:no_opportunities#1].
- Whether the March usage statement issue was resolved. The note says "Grace to chase the missing statement" (reported) [note:N-010]. No 2026-03 usage rows exist, so those months are unknown, not zero [gap:missing_month#1].
- Whether the WIDGETS overage was billed [calc:usage_trend#29].

## Suggested next steps
- Ask Grace Okafor now whether any notice on K-0008 was sent before 2026-10-01 [calc:contract_status#3] [client:C005].
- Before 2026-11-30, confirm the client's renewal intent and open a renewal opportunity, since none is recorded [calc:opportunities#1] [gap:no_renewal_opportunity#1].
- Close the reported March statement issue and check the 2026-03 usage gap [note:N-010] [gap:missing_month#1].
- Check whether the indicative EUR 240 WIDGETS overage was billed [calc:usage_trend#29], and ask why the term was shortened to 12 months [calc:contract_status#5].

## Verification

All 34 numbers and 34 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

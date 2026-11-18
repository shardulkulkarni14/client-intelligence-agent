# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The main risk is contractual, not behavioural. Contract K-0008 ends on 2026-11-30 and auto-renews unless notice is given, and the notice deadline of 2026-10-01 has already passed with no record of notice either way [calc:contract_status#1] [calc:contract_status#2] [calc:contract_status#3]. Usage is growing, so the data shows no sign of shrinkage [calc:usage_trend#3] [calc:usage_trend#17]. Confidence is medium: the data cannot show the client's intent, and there is no renewal opportunity and no meeting since 2026-05-20 [calc:opportunities#1] [calc:meeting_notes#1].

## Warning signs
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01 [calc:contract_status#1].
- It renews automatically for 12 months from 2026-12-01 unless notice is given [contracts:K-0008] [calc:contract_status#3].
- No renewal opportunity is recorded in the CRM [calc:opportunities#1].
- Reported in a note: "They could not find their March usage statement in the portal; support ticket raised." (N-010, 2026-05-20, reported) [note:N-010].

## Signs of health
- Live Match Data Feed usage rose +6.8% year on year in Aug-Oct 2026 [calc:usage_trend#3].
- Widget usage was 101.8% of included volume in Oct 2026, an indicative EUR 240 overage that is not confirmed as billed [calc:usage_trend#23] [calc:usage_trend#29].
- No tickets were open at 2026-11-01 [calc:support_summary#13]. The P1 outage T-0194 closed in 4 days with CSAT 5 out of 5 [ticket:T-0194].
- Reported in the same note: "Widgets performing well on their website." (N-010, reported) [note:N-010].

## What we do not know
- Whether the client plans to renew, shrink or leave. No notice record, no renewal opportunity and no meeting since 2026-05-20 [calc:contract_status#3] [gap:no_renewal_opportunity#1] [calc:meeting_notes#1].
- Whether the March statement problem was resolved. March 2026 usage is missing for all four products, so it is unknown, not zero [gap:missing_month#1].
- Why Stats Archive usage fell -5.9% year on year [calc:usage_trend#10]. The data does not say.
- Whether the EUR 240 overage was billed [calc:usage_trend#29]. Data confidence is medium [calc:data_quality#1].

## Suggested next steps
- Check the contract file and correspondence to confirm whether notice was given for K-0008 by 2026-10-01. The data holds no record [calc:contract_status#3].
- Agree renewal terms with the client before 2026-11-30, when the contract auto-renews [calc:contract_status#1].
- Log a renewal opportunity in the CRM, since none exists [calc:opportunities#1].
- Chase the missing March usage statement that note N-010 assigns to you [note:N-010].
- Confirm whether the indicative EUR 240 widget overage was billed before raising any expansion conversation [calc:usage_trend#29].

## Verification

All 25 numbers and 30 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

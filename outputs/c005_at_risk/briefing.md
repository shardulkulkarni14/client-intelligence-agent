# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
Usage is not shrinking, so the main risk is the contract. K-0008 ends in 29 days [calc:contract_status#1], auto-renews unless notice was given, and its notice deadline has already passed with no record either way [calc:contract_status#3]. Confidence is medium: March 2026 usage is missing and no renewal conversation is recorded [gap:missing_month#1] [gap:no_renewal_opportunity#1], so the data cannot show whether the client plans to leave.

## Warning signs
- K-0008 ends on 2026-11-30 and auto-renews for 12 months unless notice is given [calc:contract_status#1] [calc:contract_status#3]. The term was 24 months on K-0007 and is now 12 months [calc:contract_status#5].
- The notice deadline of 2026-10-01 passed 31 days before 2026-11-01 [calc:contract_status#2].
- No renewal opportunity is recorded [calc:opportunities#1].
- Widgets used 101.8% of its included volume in Oct 2026 [calc:usage_trend#23]. The overage is estimated at an indicative EUR 240, with no billing data to confirm it was charged [calc:usage_trend#29].

## Signs of health
- Aug-Oct 2026 usage against the year before: LIVE_DATA +6.8% [calc:usage_trend#3], STREAM +3.9% [calc:usage_trend#17], WIDGETS +5.5% [calc:usage_trend#24]. STATS_ARCHIVE fell -5.9% [calc:usage_trend#10].
- Usage was above included volume in 0 of 12 months for LIVE_DATA [calc:usage_trend#7], STATS_ARCHIVE [calc:usage_trend#14] and STREAM [calc:usage_trend#21].
- No open tickets [calc:support_summary#13]. Average CSAT over 12 months is 4.2 out of 5 from 6 rated tickets [calc:support_summary#5].
- Reported by Grace Okafor: "Widgets performing well on their website" [note:N-010].

## What we do not know
- Whether the client intends to renew, shrink or leave. No renewal opportunity or CRM opportunity is on file [gap:no_opportunities#1].
- Whether notice was given before the deadline. The data holds no record [calc:contract_status#3].
- Usage for March 2026 on all four products. It is unknown, not zero [gap:missing_month#1] [gap:missing_month#2] [gap:missing_month#3] [gap:missing_month#4].
- Whether the widget overage was billed [calc:usage_trend#29].
- Overall data confidence is medium [calc:data_quality#1].

## Suggested next steps
- Ask Grace Okafor, the account owner [client:C005], whether notice was given by 2026-10-01 and what renewal terms the client expects before 2026-11-30 [calc:contract_status#2].
- Contact the client before 2026-11-30 to confirm renewal intent, since the contract auto-renews [contracts:K-0008].
- Check the reported missing March usage statement and the follow-up Grace was to chase [note:N-010].
- Confirm billing for the estimated widget overage before raising it with the client [calc:usage_trend#29].

## Verification

All 27 numbers and 34 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

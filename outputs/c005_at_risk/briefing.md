# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The account is at real risk of shrinking or leaving, mainly because of its renewal position, not its usage. Contract K-0008 ends in 29 days and renews automatically unless notice was given [calc:contract_status#1], and the notice deadline has passed with no record of notice either way [calc:contract_status#3]. Confidence is medium: the renewal facts are measured, but the data cannot show whether the client intends to stay.

## Warning signs
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01 [calc:contract_status#1]. No renewal opportunity is recorded, so the contract auto-renews by default [calc:opportunities#1].
- The notice deadline was 2026-10-01 and passed 31 days before 2026-11-01 [calc:contract_status#2]. The data holds no record of notice either way [calc:contract_status#3].
- The term fell from 24 months on K-0007 to 12 months on K-0008 [calc:contract_status#5].
- A note written by Grace Okafor reports: "They could not find their March usage statement in the portal; support ticket raised." [note:N-010]. This is a reported claim, not a measured fact.

## Signs of health
- No open tickets at 2026-11-01 [calc:support_summary#13]. Ticket volume is unchanged: 1 in the last 90 days versus 1 in the previous 90 days [calc:support_summary#12].
- Usage is up year on year for Live Match Data Feed, +6.8% [calc:usage_trend#3], and Live Streaming, +3.9% [calc:usage_trend#17]. Historical Stats Archive is down, -5.9% [calc:usage_trend#10].
- Match Visualisation Widgets reached 101.8% of its included volume in Oct 2026 [calc:usage_trend#23]. This is an estimated overage of 0.8 widget impressions (millions), an indicative EUR 240 [calc:usage_trend#29].
- A note reports: "Widgets performing well on their website." [note:N-010]. This is also a reported claim.

## What we do not know
- Whether the client gave notice before 2026-10-01 [calc:contract_status#3].
- Usage for 2026-03 is unknown, not zero, for all four products [gap:missing_month#1]. That is the same month as the reported statement problem [note:N-010].
- Whether the widget overage was billed; there is no billing data [calc:usage_trend#29].
- Data confidence is medium, with no opportunity on file [calc:data_quality#1]. The only meeting on record was 165 days before 2026-11-01 [calc:meeting_notes#1].

## Suggested next steps
- Ask Grace Okafor, the account owner [client:C005], whether any notice was received before 2026-10-01 [calc:contract_status#2].
- Open a renewal opportunity now, because none is recorded and the contract ends on 2026-11-30 [calc:opportunities#1][calc:contract_status#1].
- Confirm whether the March usage statement was sent, since Grace was to chase it [note:N-010]. Fill the missing March usage rows [gap:missing_month#1].
- Book a check-in before renewal. The last meeting was on 2026-05-20 [calc:meeting_notes#1].

## Verification

All 28 numbers and 29 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

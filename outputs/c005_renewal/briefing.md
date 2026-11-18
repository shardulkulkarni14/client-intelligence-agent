# Client briefing: Marrowfield Sports Network (C005), renewal

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
Contract K-0008 ends on 2026-11-30 and auto-renews for 12 months at EUR 363,000 a year unless notice was given [contracts:K-0008] [calc:contract_status#1]. The notice deadline of 2026-10-01 has passed, and the data holds no record of notice either way, so whether the contract rolls over cannot be confirmed [calc:contract_status#3]. Usage and support look sound, so the main risks are the unconfirmed notice position and the lack of a renewal opportunity. Confidence is medium [calc:data_quality#1].

## Contract and renewal position
- K-0008 runs 2025-12-01 to 2026-11-30 at an annual value of EUR 363,000, up +4.3% on EUR 348,000 for K-0007 [contracts:K-0008] [calc:contract_status#4]
- The term shortened from 24 months on K-0007 to 12 months on K-0008 [calc:contract_status#5]
- The notice deadline passed 31 days before 2026-11-01 [calc:contract_status#2]
- No renewal opportunity is recorded in CRM [gap:no_renewal_opportunity#1]

## Usage against what they pay for
- Widgets used 44.8 widget impressions (millions) in Oct 2026 against 44.0 included, a utilisation of 101.8% [calc:usage_trend#23]
- Widgets exceeded the included volume in 2 of 12 months, including 1 of 3 in Aug-Oct 2026 [calc:usage_trend#28]
- Live Streaming peaked at 88.9% in Sep 2026 [calc:usage_trend#20]
- Live Match Data Feed used 4,223 API calls (thousands) in Oct 2026 against 5,500 included, a utilisation of 76.8% [calc:usage_trend#2]

## Risks to the renewal
- A note reports: "They could not find their March usage statement in the portal; support ticket raised." [note:N-010]
- The same note records an open action on the missing statement, with no status given [note:N-010]
- The last meeting was 2026-05-20, 165 days before 2026-11-01 [calc:meeting_notes#1]
- Widgets overage of about EUR 240 is indicative only and there is no billing data to confirm it was charged [calc:usage_trend#29]

## Room to grow
- The client holds 4 of 8 catalogue products [calc:whitespace#1]
- In-play Odds Feed (ODDS_LIVE) has an indicative entry price of EUR 75,000 per year; its prerequisite, LIVE_DATA, is already held [product:ODDS_LIVE]
- Fan Engagement Analytics (FAN_INSIGHTS) has an indicative entry price of EUR 17,500 per year and is often bought with STREAM and WIDGETS, both held [product:FAN_INSIGHTS]

## Suggested next steps
- Confirm from the contract records whether notice was given before 2026-10-01; the data cannot show it [calc:contract_status#3]
- Record a renewal opportunity in CRM, since none exists for the 2026-11-30 end date [gap:no_opportunities#1] [contracts:K-0008] [calc:contract_status#1]
- Close the open action in N-010 on the missing March usage statement, and confirm whether the support ticket was resolved [note:N-010]
- Check with billing whether the indicative EUR 240 widgets overage was charged [calc:usage_trend#29]
- Use the renewal conversation to position FAN_INSIGHTS, given its fit with STREAM and WIDGETS [product:FAN_INSIGHTS]

## Verification

All 39 numbers and 27 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Tools that found no data for this client: opportunities.

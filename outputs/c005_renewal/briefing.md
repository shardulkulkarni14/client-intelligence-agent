# Client briefing: Marrowfield Sports Network (C005), renewal

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
Contract K-0008 (EUR 363,000 a year) ends on 2026-11-30 and renews automatically for 12 months unless notice was given. The notice deadline of 2026-10-01 has passed, and the data holds no record of notice either way, so the renewal is likely to roll over at the current value but is not confirmed. Confidence is medium. [contracts:K-0008] [calc:contract_status#1] [calc:contract_status#3] [calc:data_quality#1]

## Contract and renewal position
- K-0008 is worth EUR 363,000 a year, up +4.3% on EUR 348,000 for K-0007. [contracts:K-0008] [calc:contract_status#4]
- The term fell from 24 months on K-0007 to 12 months on K-0008. [calc:contract_status#5]
- The notice deadline of 2026-10-01 passed 31 days before 2026-11-01. [calc:contract_status#2]
- No renewal opportunity is recorded in the CRM. [calc:opportunities#1] [gap:no_renewal_opportunity#1]

## Usage against what they pay for
- Widget impressions reached 101.8% of the included volume in Oct 2026 (44.8 widget impressions (millions) used against 44.0 included), and were over the included volume in 2 of the 12 months with data between Oct 2025 and Oct 2026. [calc:usage_trend#23] [calc:usage_trend#28]
- The indicative overage for Oct 2026 is EUR 240, but there is no billing data to confirm it was charged. [calc:usage_trend#29]
- Live Streaming peaked at 88.9% utilisation in Sep 2026. [calc:usage_trend#20]
- March 2026 usage is missing for all four products, so those months are not in any total. [gap:missing_month#1]

## Risks to the renewal
- The last meeting was 2026-05-20, 165 days before 2026-11-01. [calc:meeting_notes#1]
- A note by Grace Okafor reports that the client could not find its March usage statement and that a ticket was raised; the note's action was "Grace to chase the missing statement", with no record of it closing. [note:N-010]
- A P1 outage ("Feed unavailable for 20 minutes") was opened on 2026-03-20 and closed after 4 days. [ticket:T-0194]
- Average CSAT over 12 months is 4.2 out of 5, from 6 rated tickets. [calc:support_summary#5]

## Room to grow
- ODDS_LIVE (In-play Odds Feed) has an indicative entry price of EUR 75,000 per year. Its prerequisite, LIVE_DATA, is already held, but no segment peer holds it. [product:ODDS_LIVE]
- FAN_INSIGHTS (Fan Engagement Analytics) has an indicative entry price of EUR 17,500 per year. It is held by 2 of 5 segment peers and is often bought alongside STREAM and WIDGETS, which the client already holds. [product:FAN_INSIGHTS]

## Suggested next steps
- Confirm with the account owner, Grace Okafor, whether notice was given before the 2026-10-01 deadline. [calc:contract_status#2] [client:C005]
- Record a renewal opportunity now, since none exists and K-0008 ends on 2026-11-30. [gap:no_renewal_opportunity#1] [contracts:K-0008]
- Check whether the indicative EUR 240 widget overage was billed. [calc:usage_trend#29]
- Close the open March statement follow-up from note N-010 and confirm the client has the statement. [note:N-010]
- Obtain the missing March 2026 usage rows before using usage figures in the renewal proposal. [gap:missing_month#1]

## Verification

All 43 numbers and 28 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Tools that found no data for this client: opportunities.

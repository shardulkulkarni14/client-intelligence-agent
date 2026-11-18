# Client briefing: Marrowfield Sports Network (C005), renewal

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The notice deadline for K-0008 passed on 2026-10-01, and the data holds no record of notice either way. If no notice was given, the contract would roll over for another 12 months from 2026-12-01 at the current annual value of EUR 363,000 [calc:contract_status#3] [contracts:K-0008]. Confidence is medium because of missing March usage and no renewal opportunity on file [calc:data_quality#1].

## Contract and renewal position
- K-0008 runs 2025-12-01 to 2026-11-30 and ends 29 days after 2026-11-01 [contracts:K-0008] [calc:contract_status#1].
- The notice deadline was 2026-10-01 and passed 31 days before 2026-11-01 [calc:contract_status#2].
- The annual value is up +4.3% on the previous contract's EUR 348,000 [calc:contract_status#4]. The term fell from 24 months to 12 months [calc:contract_status#5].
- No renewal opportunity is recorded in the CRM [gap:no_renewal_opportunity#1] [gap:no_opportunities#1].

## Usage against what they pay for
- WIDGETS used 44.8 widget impressions (millions) in Oct 2026 against 44.0 included, a utilisation of 101.8% [calc:usage_trend#23]. The estimated overage is an indicative EUR 240, with no billing data to confirm it was charged [calc:usage_trend#29].
- STREAM reached 88.9% utilisation in Sep 2026 and 79.4% in Oct 2026 [calc:usage_trend#20] [calc:usage_trend#16].
- LIVE_DATA usage rose +6.8% year on year for Aug-Oct 2026 and reached 76.8% utilisation in Oct 2026 [calc:usage_trend#3] [calc:usage_trend#2].
- March 2026 usage is missing for four products, so it is unknown, not zero [gap:missing_month#1].

## Risks to the renewal
- Whether notice was given is unknown, and that decides whether the auto-renewal applies [calc:contract_status#3].
- A P1 outage ticket, "Feed unavailable for 20 minutes", was opened 2026-03-20 and closed after 4 days [ticket:T-0194].
- Note N-010 from Grace Okafor on 2026-05-20 reports: "They could not find their March usage statement in the portal; support ticket raised." This is a reported claim [note:N-010].
- The last meeting was 165 days before 2026-11-01 [calc:meeting_notes#1]. The data does not show whether the statement action was closed [note:N-010].

## Room to grow
- Fan Engagement Analytics (FAN_INSIGHTS) is not held. It is held by 2 of 5 segment peers, is often bought with STREAM and WIDGETS, and has an indicative entry price of EUR 17,500 per year [product:FAN_INSIGHTS].
- In-play Odds Feed (ODDS_LIVE) is not held. LIVE_DATA, its prerequisite, is already held. The indicative price is EUR 75,000 per year, and no segment peer holds it [product:ODDS_LIVE].

## Suggested next steps
- Confirm with Grace Okafor and the contract file whether notice was sent for K-0008 [client:C005] [calc:contract_status#3].
- Open a renewal opportunity in the CRM before the 2026-11-30 end date [calc:opportunities#1].
- Check whether the WIDGETS overage was billed and close the March usage statement ticket [calc:usage_trend#29] [note:N-010].
- Discuss the drop from 24 to 12 months with the client before renewal terms are set [calc:contract_status#5].

## Verification

All 42 numbers and 30 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Tools that found no data for this client: opportunities.

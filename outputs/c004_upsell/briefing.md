# Client briefing: Quillon Esports (C004), upsell

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Growth looks more likely from new products than from more of Live Match Data Feed, because the one product held is only 40.0% used and 7 of 8 catalogue products are not held [calc:usage_trend#2] [calc:whitespace#1]. Confidence is low: the usage history is two months and the peer group has two clients [calc:data_quality#1] [gap:small_peer_group#1]. Match Visualisation Widgets and In-play Odds Feed are both often bought with the held product, and the prerequisite for Odds is already in place [product:WIDGETS] [product:ODDS_LIVE].

## More of what they already use
- Oct 2026 utilisation is 40.0%: 800 of 2,000 API calls (thousands) included [calc:usage_trend#2].
- The Sep-Oct average of 33.1% covers only two months, so the trend is unclear [calc:usage_trend#3] [gap:short_history#1].
- Usage has never exceeded the included volume [calc:usage_trend#5]. There is no overage signal to build on.

## Products they do not hold
- Match Visualisation Widgets: indicative EUR 30,000 per year, often bought with LIVE_DATA, held by both segment peers [product:WIDGETS].
- In-play Odds Feed: indicative EUR 75,000 per year, often bought with LIVE_DATA, prerequisite already held [product:ODDS_LIVE].
- Historical Stats Archive: indicative EUR 20,000 per year, held by both segment peers [product:STATS_ARCHIVE].
- Not typically sold to Fantasy & Gaming: Fan Engagement Analytics EUR 17,500 [product:FAN_INSIGHTS], Integrity Monitoring EUR 25,000 [product:INTEGRITY], Pre-match Odds EUR 45,000 [product:ODDS_PRE], Live Streaming EUR 55,000 [product:STREAM].

## What could block the pitch
- Idle capacity: at 40.0% utilisation, a bigger LIVE_DATA-linked deal invites the question of why current capacity is unused [calc:usage_trend#2].
- Thin relationship: the client has been a customer since 2026-09-01 [client:C004], and no meeting notes exist [gap:no_meeting_notes#1].
- Weak peer evidence: peer holdings are based on two clients [product:WIDGETS] [gap:small_peer_group#1].
- Service health is unknown: no support tickets are recorded, which is not the same as no problems [gap:no_support_tickets#1].

## Timing
- Contract K-0006 runs 2026-09-01 to 2027-08-31 at EUR 48,000 a year [contracts:K-0006].
- It renews automatically unless notice is given 30 days before the end date, so the notice deadline is 2027-08-01 [contracts:K-0006] [calc:contract_status#2].
- The contract ends in 303 days from 2026-11-01 [calc:contract_status#1].
- The CRM next step reads "Signed" for the closed opportunity (reported), and the contract confirms the deal is in force [opp:O-0004] [contracts:K-0006].

## Suggested next steps
- Review LIVE_DATA usage with Elif Aydin before pitching anything new, since utilisation is 40.0% [calc:usage_trend#2] [client:C004].
- Lead with Match Visualisation Widgets as the add-on bought with LIVE_DATA, at EUR 30,000 per year [product:WIDGETS].
- Schedule the renewal conversation before the notice deadline of 2027-08-01 [calc:contract_status#2].
- Ask the account team to record meeting notes and support status, since neither exists yet [gap:no_meeting_notes#1] [gap:no_support_tickets#1].

## Verification

All 27 numbers and 35 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): only 2 months of usage history (fewer than 12), so no year-on-year comparison is possible. [gap:short_history#1][usage:U-00265][usage:U-00266]
- Only 2 other clients in segment Fantasy & Gaming; peer adoption is a weak comparison and no percentage is given. [gap:small_peer_group#1][client:C006][client:C019]
- Contract K-0006 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0006]
- No meeting notes exist for this client, so there is no relationship context from notes. [gap:no_meeting_notes#1]
- No support tickets are recorded for this client. That means no ticket data, not that the client has no problems. [gap:no_support_tickets#1]
- Tools that found no data for this client: meeting_notes, support_summary.

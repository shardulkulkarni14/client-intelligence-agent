# Client briefing: Quillon Esports (C004), upsell

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Growth is more likely to come from new products than from more usage. Quillon used 40.0% of its included volume in Oct 2026 and has never gone over it [calc:usage_trend#2][calc:usage_trend#5]. It holds 1 of 8 catalogue products [calc:whitespace#1], and WIDGETS and STATS_ARCHIVE are held by both segment peers [product:WIDGETS][product:STATS_ARCHIVE]. Confidence is low: there are only 2 months of usage history and 2 peers [calc:data_quality#1].

## More of what they already use
- Oct 2026 usage was 800 API calls (thousands) against 2,000 included, a utilisation of 40.0% [calc:usage_trend#2].
- Average utilisation for Sep-Oct 2026 was 33.1%, but this covers only 2 months of history [calc:usage_trend#3][gap:short_history#1].
- Usage did not exceed the included volume in either month, so there is no overage to convert into a volume upgrade [calc:usage_trend#5][contracts:K-0006].

## Products they do not hold
- Match Visualisation Widgets (EUR 30,000 per year): held by 2 of 2 segment peers and often bought with LIVE_DATA [product:WIDGETS].
- Historical Stats Archive (EUR 20,000 per year): held by 2 of 2 segment peers and typically sold to Fantasy & Gaming [product:STATS_ARCHIVE].
- In-play Odds Feed (EUR 75,000 per year): often bought with LIVE_DATA, and its prerequisite is already held, but no peer holds it [product:ODDS_LIVE]. This is a pairing pitch, not a peer-proven one.
- Fan Engagement Analytics (EUR 17,500), Integrity Monitoring (EUR 25,000), Pre-match Odds Feed (EUR 45,000) and Live Streaming (EUR 55,000) are not held by any peer and not typically sold to this segment [product:FAN_INSIGHTS][product:INTEGRITY][product:ODDS_PRE][product:STREAM].

## What could block the pitch
- Peer evidence is thin: only 2 other clients in the segment, so peer adoption is a weak argument [calc:whitespace#2][gap:small_peer_group#1].
- A volume-led pitch is unlikely to land, since usage is well below included volume [calc:usage_trend#2].
- The account is new, with the customer since 2026-09-01 [client:C004], so there is no year-on-year trend to show [gap:short_history#1].
- No meeting notes or support tickets exist, so relationship context and problem signals are unknown [gap:no_meeting_notes#1][gap:no_support_tickets#1].

## Timing
- Contract K-0006 runs 2026-09-01 to 2027-08-31 at an annual value of EUR 48,000 [contracts:K-0006].
- It renews automatically unless notice is given, and the notice deadline is 2027-08-01 [contracts:K-0006][calc:contract_status#2].
- The CRM next step on the LIVE_DATA deal reads "Signed" (reported), which agrees with the Closed Won stage [opp:O-0004].

## Suggested next steps
- Lead with WIDGETS as the first product conversation, since both peers hold it and it is often bought with LIVE_DATA [product:WIDGETS].
- Treat ODDS_LIVE (EUR 75,000 per year) as a later pairing proposal, and say plainly that no peer holds it [product:ODDS_LIVE].
- Before the notice deadline of 2027-08-01, review usage again once more months of data exist [calc:contract_status#2][gap:short_history#1].
- Add a meeting note so the relationship context is recorded [gap:no_meeting_notes#1].

## Verification

All 32 numbers and 34 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- LIVE_DATA (Live Match Data Feed): only 2 months of usage history (fewer than 12), so no year-on-year comparison is possible. [gap:short_history#1][usage:U-00265][usage:U-00266]
- Only 2 other clients in segment Fantasy & Gaming; peer adoption is a weak comparison and no percentage is given. [gap:small_peer_group#1][client:C006][client:C019]
- Contract K-0006 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0006]
- No meeting notes exist for this client, so there is no relationship context from notes. [gap:no_meeting_notes#1]
- No support tickets are recorded for this client. That means no ticket data, not that the client has no problems. [gap:no_support_tickets#1]
- Tools that found no data for this client: meeting_notes, support_summary.

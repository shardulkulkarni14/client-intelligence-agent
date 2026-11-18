# Client briefing: Quillon Esports (C004), upsell

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Growth is more likely through new products than through more volume: Quillon holds 1 of 8 catalogue products [calc:whitespace#1], and usage is well under the included volume [calc:usage_trend#2]. Confidence is low, because only two months of usage and a two-client peer group are on file [calc:data_quality#1] [gap:short_history#1] [gap:small_peer_group#1].

## More of what they already use
- Live Match Data Feed used 800 API calls (thousands) in Oct 2026 against 2,000 included, a utilisation of 40.0% [calc:usage_trend#2].
- The two-month average is 33.1%, with 1,323 API calls (thousands) used against 4,000 included [calc:usage_trend#3]. Usage was above the included volume in 0 of the last 2 months [calc:usage_trend#5].
- Treat this as headroom, not proven demand, since the history is only two months [gap:short_history#1].

## Products they do not hold
- In-play Odds Feed (ODDS_LIVE) is the largest entry price at EUR 75,000 per year. It is often bought with held LIVE_DATA, and its prerequisite is already held, but it is not typically sold to Fantasy & Gaming and no peer holds it [product:ODDS_LIVE].
- Match Visualisation Widgets (WIDGETS) is EUR 30,000 per year, is often bought with LIVE_DATA, and is held by both segment peers. The peer evidence is weak [product:WIDGETS] [gap:small_peer_group#1].
- Historical Stats Archive (STATS_ARCHIVE) is EUR 20,000 per year and is held by both segment peers [product:STATS_ARCHIVE].
- Fan Engagement Analytics, Integrity Monitoring, Pre-match Odds Feed and Live Streaming are not typically sold to the segment and no peer holds them [product:FAN_INSIGHTS] [product:INTEGRITY] [product:ODDS_PRE] [product:STREAM].

## What could block the pitch
- Low data confidence means any volume or product case rests on a short history [calc:data_quality#1].
- With usage under the included volume, a pitch for more volume is hard to justify on current data [calc:usage_trend#2].
- No meeting notes exist, so the relationship context and client priorities are unknown [gap:no_meeting_notes#1].

## Timing
- Contract K-0006 runs 2026-09-01 to 2027-08-31 at an annual value of EUR 48,000 [contracts:K-0006].
- It renews automatically unless notice is given 30 days before the end date. The notice deadline is 2027-08-01 [contracts:K-0006] [calc:contract_status#2].
- The contract ends 303 days after 2026-11-01 [calc:contract_status#1].

## Suggested next steps
- Ask Elif Aydin to review Live Match Data Feed usage against the included volume before proposing more volume, starting from 40.0% in Oct 2026 [calc:usage_trend#2].
- Open the ODDS_LIVE conversation first, since it builds on the held LIVE_DATA [product:ODDS_LIVE]. Test WIDGETS as an alternative because it is often bought with LIVE_DATA [product:WIDGETS].
- Plan the proposal to land before the notice deadline of 2027-08-01 [calc:contract_status#2].
- Record meeting notes with the client to fill the relationship gap [gap:no_meeting_notes#1].

## Verification

All 24 numbers and 29 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- LIVE_DATA (Live Match Data Feed): only 2 months of usage history (fewer than 12), so no year-on-year comparison is possible. [gap:short_history#1][usage:U-00265][usage:U-00266]
- Only 2 other clients in segment Fantasy & Gaming; peer adoption is a weak comparison and no percentage is given. [gap:small_peer_group#1][client:C006][client:C019]
- Contract K-0006 is the only signed contract on file, so the change in annual value at the last renewal cannot be computed. [gap:no_previous_contract#1][contracts:K-0006]
- No meeting notes exist for this client, so there is no relationship context from notes. [gap:no_meeting_notes#1]
- No support tickets are recorded for this client. That means no ticket data, not that the client has no problems. [gap:no_support_tickets#1]
- Tools that found no data for this client: meeting_notes, support_summary.

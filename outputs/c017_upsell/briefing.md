# Client briefing: Wexley Athletic FC (C017), upsell

_Data as of 2026-11-01. Account owner: Maya Lindgren._

## Bottom line
The clearest growth is more use of what Wexley already holds. Historical Stats Archive and Match Visualisation Widgets are rising and close to their included volumes, while Fan Engagement Analytics is flat and under-used. Live Match Data Feed is the most plausible new product, but the data shows no demand for any unheld product and the peer comparison is too thin to confirm one. Confidence is moderate.

## More of what they already use
- Historical Stats Archive is the strongest signal: Aug-Oct 2026 usage is up year on year, and Oct 2026 use is near its included volume [calc:usage_trend#10] [calc:usage_trend#9].
- Usage has not exceeded included volume in any of the last 12 months, so there is headroom but no overage yet [calc:usage_trend#14].
- Match Visualisation Widgets is also growing, at +9.6% year on year in Aug-Oct 2026 with 73.3% utilisation in Oct 2026 [calc:usage_trend#17] [calc:usage_trend#16].
- Fan Engagement Analytics is the weak spot: 5 active dashboard users against 8 included in Oct 2026, and flat year on year [calc:usage_trend#2] [calc:usage_trend#3]. Pitch adoption here, not more seats.

## Products they do not hold
- Live Match Data Feed (LIVE_DATA) is the natural first pitch. It is often bought alongside held WIDGETS, with an indicative entry price of EUR 60,000 per year [product:LIVE_DATA].
- Live Streaming (STREAM, EUR 55,000 per year) fits held FAN_INSIGHTS and WIDGETS, but it was lost before. The CRM note reads "Lost - rights held by league" [product:STREAM] [opp:O-0014].
- In-play Odds Feed (ODDS_LIVE, EUR 75,000 per year) requires LIVE_DATA, so it can only follow that sale [product:ODDS_LIVE].
- Pre-match Odds Feed (ODDS_PRE, EUR 45,000) and Integrity Monitoring (INTEGRITY, EUR 25,000) have no specific signal in the data [product:ODDS_PRE] [product:INTEGRITY].

## What could block the pitch
- The STREAM loss was recorded as rights-related, but whether the rights position has changed is not known [opp:O-0014].
- Service history is mixed. There were 3 P1/P2 tickets in the last 12 months [calc:support_summary#4], and the CSAT of 4.0 rests on one rated ticket [calc:support_summary#5].
- The contract rose +3.8% at renewal, so price will be sensitive [calc:contract_status#3].
- No meeting notes exist, so relationship context is missing [gap:no_meeting_notes#1]. The peer group is one client, so there is no reliable adoption benchmark [gap:small_peer_group#1].

## Timing
- Contract K-0030 runs to 2027-06-30 and renews automatically unless notice is given [contracts:K-0030].
- The notice deadline is 2027-05-31, 211 days after 2026-11-01 [calc:contract_status#2].
- Support is quieting: 0 tickets in the last 90 days versus 1 in the previous 90 days [calc:support_summary#8].

## Suggested next steps
- Build a Stats Archive and Widgets expansion case using the year-on-year growth [calc:usage_trend#10] [calc:usage_trend#17].
- Work on Fan Engagement Analytics adoption before any seat upsell, given 5 of 8 used [calc:usage_trend#2].
- Use the client's usage-breakdown request as an entry point for usage reporting [ticket:T-0207].
- Open the LIVE_DATA conversation through the WIDGETS relationship, at an indicative EUR 60,000 per year [product:LIVE_DATA].
- Confirm the league rights position before raising STREAM again [opp:O-0014].
- Diary the notice deadline of 2027-05-31 [calc:contract_status#2].

## Verification

All 31 numbers and 29 citations were checked against the evidence.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- Only 1 other client in segment Club; peer adoption is a weak comparison and no percentage is given. [gap:small_peer_group#1][client:C022]
- No meeting notes exist for this client, so there is no relationship context from notes. [gap:no_meeting_notes#1]
- Tools that found no data for this client: meeting_notes.

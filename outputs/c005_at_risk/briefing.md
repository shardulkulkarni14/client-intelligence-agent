# Client briefing: Marrowfield Sports Network (C005), at_risk

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
The main risk is contract timing, not visible decline. Contract K-0008 ends 2026-11-30, 29 days after 2026-11-01 [calc:contract_status#1], and its notice deadline passed 31 days before 2026-11-01 with no record of notice either way [calc:contract_status#2][calc:contract_status#3]. Usage and support data show no measured sign of shrinking, but a reported complaint and the lack of recent contact leave the renewal position unclear. Confidence is medium: the dates are firm, but whether notice was given and the client's intent are not in the data [calc:data_quality#1].

## Warning signs
- K-0008 renews automatically for the same 12-month term unless notice is given [contracts:K-0008] [calc:contract_status#3].
- The notice window closed on 2026-10-01, and nothing on record shows whether notice was sent [calc:contract_status#2].
- The term shortened from 24 months on K-0007 to 12 months on K-0008 [calc:contract_status#5].
- Reported by Grace Okafor on 2026-05-20: the client "could not find their March usage statement in the portal; support ticket raised" [note:N-010].

## Signs of health
- No open tickets at 2026-11-01, and 1 ticket in the last 90 days versus 1 in the previous 90 days [calc:support_summary#13] [calc:support_summary#12].
- Average CSAT is 4.2 out of 5 over the last 12 months [calc:support_summary#5].
- Year-on-year usage is up on Live Match Data Feed (+6.8%) and Live Streaming (+3.9%) [calc:usage_trend#3] [calc:usage_trend#17]. Historical Stats Archive is down (-5.9%) [calc:usage_trend#10].
- Widget use reached 101.8% of included volume in Oct 2026 [calc:usage_trend#23]. The estimated overage of EUR 240 is indicative only and no billing data confirms it was charged [calc:usage_trend#29].

## What we do not know
- Whether notice was given on or before the deadline. No record exists either way [calc:contract_status#3].
- Whether any renewal opportunity exists. None is recorded [gap:no_renewal_opportunity#1]. The last meeting was 165 days before 2026-11-01 [calc:meeting_notes#1].
- Usage for 2026-03 is missing on all four usage lines. Those months are unknown, not zero [gap:missing_month#1].
- Whether the March statement issue was resolved, or whether the commitment to chase it was completed [note:N-010].

## Suggested next steps
- Check whether a notice was sent for K-0008 by the 2026-10-01 deadline, since the record cannot show it [calc:contract_status#2].
- With 29 days left before the end date, open a renewal conversation and record it as an opportunity, since none is on file [calc:contract_status#1] [gap:no_opportunities#1].
- Close out the March usage statement issue you committed to chase in the 2026-05-20 note [note:N-010].
- Confirm with billing whether the widget overage was charged before raising it with the client, given the term change to 12 months [calc:usage_trend#29] [calc:contract_status#5].

## Verification

All 31 numbers and 28 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

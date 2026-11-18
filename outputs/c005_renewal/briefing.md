# Client briefing: Marrowfield Sports Network (C005), renewal

_Data as of 2026-11-01. Account owner: Grace Okafor._

## Bottom line
Renewal is effectively automatic. Contract K-0008 (annual value EUR 363,000 [contracts:K-0008]) ends 2026-11-30, and the notice deadline of 2026-10-01 has passed [calc:contract_status#2]. Whether notice was given is not known, and no renewal opportunity is on file [calc:contract_status#3] [gap:no_renewal_opportunity#1]. Confidence is medium [calc:data_quality#1].

## Contract and renewal position
- K-0008 auto-renews for the same 12-month term unless notice is given. The deadline passed 31 days before 2026-11-01 [contracts:K-0008] [calc:contract_status#2].
- Without notice, the contract rolls over for 12 months from 2026-12-01 [calc:contract_status#3].
- Annual value is EUR 363,000, up +4.3% on EUR 348,000 for K-0007 [calc:contract_status#4].
- The term was cut from 24 months to 12 months, which shortens the next renewal cycle [calc:contract_status#5].

## Usage against what they pay for
- WIDGETS reached 101.8% of its included volume in Oct 2026 (44.8 against 44.0) and exceeded it in 2 of the last 12 months [calc:usage_trend#23] [calc:usage_trend#28].
- The indicative overage for WIDGETS in Oct 2026 is EUR 240. There is no billing data to confirm it was charged [calc:usage_trend#29].
- LIVE_DATA was at 76.8% of included volume in Oct 2026 and up +6.8% year on year in Aug-Oct [calc:usage_trend#2] [calc:usage_trend#3].
- STREAM peaked at 88.9% of included volume in Sep 2026 [calc:usage_trend#20].

## Risks to the renewal
- Support: one P1 outage in the last 12 months, "Feed unavailable for 20 minutes" [ticket:T-0194]. Average CSAT is 4.2 out of 5 from 6 rated tickets [calc:support_summary#5].
- Reported in a 2026-05-20 note by Grace Okafor: the client "could not find their March usage statement in the portal" [note:N-010].
- The last meeting was 165 days before 2026-11-01 [calc:meeting_notes#1].
- March 2026 usage is missing for all four products, so those months are unknown, not zero [gap:missing_month#1].

## Room to grow
- Fan Engagement Analytics (FAN_INSIGHTS) is not held, is held by 2 of 5 peers, and is often bought with STREAM and WIDGETS. Indicative entry price is EUR 17,500 per year [product:FAN_INSIGHTS].
- In-play Odds Feed (ODDS_LIVE) is not typically sold to Broadcasters, but its prerequisite LIVE_DATA is held. Indicative entry price is EUR 75,000 per year [product:ODDS_LIVE].

## Suggested next steps
- Ask Grace Okafor whether notice was given before 2026-10-01 and record the answer [calc:contract_status#2].
- Confirm with billing whether the EUR 240 WIDGETS overage was charged [calc:usage_trend#29].
- Chase the March 2026 usage statement noted in N-010, which Grace was to chase [note:N-010].
- Open a renewal opportunity in the CRM before 2026-11-30 [gap:no_renewal_opportunity#1].
- Raise the WIDGETS capacity against the 12-month term with the client [calc:usage_trend#23] [calc:contract_status#5].

## Verification

All 44 numbers and 29 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0008]
- No CRM opportunity is on file for client C005. [gap:no_opportunities#1]
- LIVE_DATA (Live Match Data Feed): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#1]
- STATS_ARCHIVE (Historical Stats Archive): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#2]
- STREAM (Live Streaming): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#3]
- WIDGETS (Match Visualisation Widgets): no usage row for 2026-03. Usage in these months is unknown, not zero, and they are left out of every total. [gap:missing_month#4]
- Tools that found no data for this client: opportunities.

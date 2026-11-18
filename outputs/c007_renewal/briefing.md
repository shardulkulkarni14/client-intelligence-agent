# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not in force and is not yet on track. Contract K-0011 expired 32 days before 2026-11-01 [calc:contract_status#1], and its replacement, K-0045 at EUR 200,000 a year, is unsigned [contracts:K-0045]. Usage supports that value, but data confidence is low, so treat this view as provisional [calc:data_quality#1].

## Contract and renewal position
- K-0011 (EUR 189,000 a year) ran 2024-10-01 to 2026-09-30 and is no longer in force [calc:contract_status#1].
- K-0045 is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year, +5.8% on K-0011, with no signed date [contracts:K-0045] [calc:contract_status#2].
- Opportunity O-0005 (EUR 200,000) is still at Negotiation, with an expected close of 2026-09-30 [opp:O-0005] [calc:opportunities#2].
- Note N-009, written by Tomas Ferreira, records that terms were "agreed commercially" and the client's legal team is reviewing the data-rights clause (reported) [note:N-009].
- The notice period is 90 days before the end date [contracts:K-0045]. The data does not calculate the notice date.

## Usage against what they pay for
- Live Match Data Feed: 9,504 API calls (thousands) in Aug-Oct 2026, +16.9% year on year [calc:usage_trend#10]. Utilisation was 72.6% in Aug-Sep 2026 [calc:usage_trend#12].
- Integrity Monitoring: 78.1% average utilisation in Aug-Sep 2026 [calc:usage_trend#5]. Its one overage month was Dec 2025 at 101.1% [calc:usage_trend#6].
- Historical Stats Archive: 73.6% utilisation in Aug-Sep 2026 [calc:usage_trend#19]. No overage months in the period [calc:usage_trend#21].

## Risks to the renewal
- The client asked for service to continue after 30 September while legal review completes (reported in N-009) [note:N-009].
- The feed is still in use. Ticket T-0276, opened 2026-10-05, asks to "Confirm feed access continues while renewal is in legal review" [ticket:T-0276].
- The data holds no record that the interim arrangement assigned to you in N-009 was confirmed [note:N-009].
- Last meeting was 52 days before 2026-11-01 [calc:meeting_notes#1]. Recent support is light and rated well: 1 ticket in 90 days, CSAT 4.0 [calc:support_summary#7] [calc:support_summary#10].

## Room to grow
- Five of eight catalogue products are not held [calc:whitespace#1].
- Live Streaming (indicative EUR 55,000 a year) is held by 4 of 5 segment peers [product:STREAM].
- In-play Odds Feed (indicative EUR 75,000 a year) builds on LIVE_DATA, which is already held [product:ODDS_LIVE].

## Suggested next steps
1. Confirm in writing the interim service arrangement for feed access. The client asked for service to continue after 30 September (reported in N-009) [note:N-009] [ticket:T-0276].
2. Push K-0045 to signature and close out the data-rights clause in legal review [contracts:K-0045] [opp:O-0005].
3. Update O-0005, which is stale at Negotiation with a past close date [calc:opportunities#2].
4. Work out the notice date from the 90-day notice period in K-0045 [contracts:K-0045].

## Verification

All 37 numbers and 31 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

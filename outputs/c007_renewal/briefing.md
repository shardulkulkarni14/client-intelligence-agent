# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
Not on track as the data stands. No contract is in force: K-0011 ended on 2026-09-30, and its replacement K-0045 (EUR 200,000 a year) is unsigned [calc:contract_status#1] [contracts:K-0045]. Confidence is low because the notice deadline is not in the data and the "terms agreed" position rests on a rep's note [calc:data_quality#1] [note:N-009].

## Contract and renewal position
- K-0011 (EUR 189,000 a year) ended 32 days before 2026-11-01 [calc:contract_status#1].
- K-0045 is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year, which is +5.8% on K-0011, but it has no signed date [contracts:K-0045] [calc:contract_status#2].
- Renewal opportunity O-0005 is still at Negotiation, with an expected close of 2026-09-30, and is stale by 32 days [opp:O-0005] [calc:opportunities#2].
- Tomas Ferreira's note of 2026-09-10 reports "Renewal terms agreed commercially," with the client's legal team reviewing the data-rights clause. This is a reported claim, not a measured fact [note:N-009].

## Usage against what they pay for
- INTEGRITY: 640 matches monitored in Aug-Oct 2026, -6.0% year on year; utilisation 78.1% in Aug-Sep 2026 [calc:usage_trend#3] [calc:usage_trend#5].
- LIVE_DATA: 9,504 API calls (thousands) in Aug-Oct 2026, +16.9% year on year; utilisation 72.6% [calc:usage_trend#10] [calc:usage_trend#12].
- STATS_ARCHIVE: 399 queries (thousands) in Aug-Oct 2026, +3.4% year on year; utilisation 73.6% [calc:usage_trend#17] [calc:usage_trend#19].
- Usage is not computed for 2026-10 against an included volume, because no signed contract covered that month [gap:blank_included_units#1].

## Risks to the renewal
- Service continuity is the client's stated condition: they want service to continue "without interruption after 30 September" while legal review completes [note:N-009]. Their ticket T-0276 asks the same thing [ticket:T-0276].
- The "terms agreed" note conflicts with the opportunity still at Negotiation and stale [note:N-009] [opp:O-0005].
- Support is not a current risk: 0 P1/P2 tickets in the last 90 days, and CSAT of 4.0 [calc:support_summary#9] [calc:support_summary#10].

## Room to grow
- Live Streaming (STREAM) is held by 4 of 5 segment peers, at an indicative EUR 55,000 a year [product:STREAM].
- Fan Engagement Analytics (FAN_INSIGHTS) is held by 4 of 5 peers, at an indicative EUR 17,500 a year [product:FAN_INSIGHTS].
- Pre-match Odds Feed (ODDS_PRE) is often bought with INTEGRITY, which they hold, at an indicative EUR 45,000 a year [product:ODDS_PRE]. Raise these only after K-0045 is signed.

## Suggested next steps
- Confirm the notice deadline and the signature date for K-0045 with the contracts team. Neither is in the data.
- Confirm the interim service arrangement that Tomas Ferreira committed to in the 2026-09-10 note [note:N-009].
- Reply to T-0276 on feed access continuity while legal review runs [ticket:T-0276].
- Update O-0005 to reflect the legal review, and correct its stage and close date [opp:O-0005] [calc:opportunities#2].

## Verification

All 38 numbers and 30 citations were checked against the evidence.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

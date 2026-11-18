# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not on track as recorded. The contract in force ended on 2026-09-30, and its replacement, K-0045, is unsigned, so no signed contract covers the account today. If K-0045 is signed as drafted, the annual value is EUR 200,000, up 5.8% on the expired EUR 189,000 [calc:contract_status#2] [calc:contract_status#1]. Confidence is low: the data is flagged low-confidence, and the "terms agreed" position rests on a note, not a signed document [calc:data_quality#1] [note:N-009].

## Contract and renewal position
- K-0011 expired. It ran 2024-10-01 to 2026-09-30 at EUR 189,000 a year and ended 32 days before 2026-11-01 [calc:contract_status#1].
- K-0045 is pending signature with no signed date. It is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year [contracts:K-0045].
- Renewal opportunity O-0005 (EUR 200,000) is still at Negotiation, with an expected close of 2026-09-30, now stale by 32 days [opp:O-0005] [calc:opportunities#2].
- Reported by Tomas Ferreira on 2026-09-10: "Renewal terms agreed commercially," with the client's legal team reviewing the data-rights clause. This is a claim, not a measurement, and it does not match an opportunity still at Negotiation [note:N-009].

## Usage against what they pay for
- Integrity Monitoring: 640 matches monitored in Aug-Oct 2026, down 6.0% year on year. Average utilisation was 78.1% in Aug-Sep 2026 [calc:usage_trend#3] [calc:usage_trend#5].
- Live Match Data Feed: 9,504 API calls (thousands) in Aug-Oct 2026, up 16.9% year on year. Utilisation was 72.6%, and usage was never above the included volume in the last 11 months with a known volume [calc:usage_trend#9] [calc:usage_trend#11] [calc:usage_trend#12].
- Historical Stats Archive: 399 queries (thousands) in Aug-Oct 2026, up 3.4% year on year. Utilisation was 73.6% [calc:usage_trend#15] [calc:usage_trend#17].
- October 2026 utilisation cannot be measured for any product, because no signed contract covered that month.

## Risks to the renewal
- Reported by Tomas Ferreira, the client wants uninterrupted service past the K-0011 end date while legal review completes. The interim arrangement is only a task for him [note:N-009] [calc:contract_status#1].
- The data-rights clause is still in legal review. The CRM next step reads "Legal review of data-rights clause" (reported) [opp:O-0005].
- The opportunity's expected close date has passed while it is still at Negotiation [calc:opportunities#2].
- The last meeting was 52 days before 2026-11-01 [calc:meeting_notes#1].
- The notice deadline is not in the data, so it is not known how much time remains.

## Room to grow
- Fan Engagement Analytics (FAN_INSIGHTS) is held by 4 of 5 segment peers, with an indicative entry price of EUR 17,500 a year [product:FAN_INSIGHTS].
- Live Streaming (STREAM) is also held by 4 of 5 peers, at an indicative EUR 55,000 a year [product:STREAM].
- Pre-match Odds Feed (ODDS_PRE) is often bought with INTEGRITY, which they already hold, at an indicative EUR 45,000 a year [product:ODDS_PRE].

## Suggested next steps
- Get Tomas Ferreira's written confirmation of the interim service arrangement for the period after K-0011 ended on 2026-09-30, which the client asked for, as reported in his note [note:N-009] [calc:contract_status#1].
- Ask the client's legal team for the review's completion date, and confirm the notice deadline directly, since the data does not include it [opp:O-0005].
- Move K-0045 toward signature, and update O-0005's stage and close date, which are 32 days stale [contracts:K-0045] [calc:opportunities#2].
- After signature, raise FAN_INSIGHTS and STREAM, the two add-ons most segment peers already hold [product:STREAM].

## Verification

All 42 numbers and 30 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation is undefined there. [usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation is undefined there. [usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation is undefined there. [usage:U-00502]
- No signed contract is in force for C007 on 2026-11-01. Contracts on file: K-0011 (expired), K-0045 (pending_signature). [contracts:K-0011][contracts:K-0045]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [contracts:K-0011]

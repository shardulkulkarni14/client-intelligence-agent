# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not on track on paper. No contract is in force: K-0011 expired on 2026-09-30, and its replacement, K-0045, is unsigned [calc:contract_status#1] [contracts:K-0045]. The proposed value is EUR 200,000 a year, +5.8% on EUR 189,000 [calc:contract_status#2]. Confidence is low because the data is incomplete [calc:data_quality#1] [gap:no_contract_in_force#1].

## Contract and renewal position
- K-0011 ran from 2024-10-01 to 2026-09-30 at EUR 189,000 a year, with a 90-day notice period. It ended 32 days before 2026-11-01 [calc:contract_status#1].
- K-0045 is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year. It has no signed date and a drafted 90-day notice period [contracts:K-0045].
- The notice window on K-0011 has passed. The K-0045 notice period applies to its end date of 2028-09-30 [calc:contract_status#1] [contracts:K-0045].
- Reported: the note says "Renewal terms agreed commercially," with legal reviewing the data-rights clause [note:N-009]. The CRM still shows O-0005 at Negotiation, with an expected close of 2026-09-30, which is stale [opp:O-0005] [calc:opportunities#2]. These do not agree.

## Usage against what they pay for
- LIVE_DATA is the largest line. It used 9,504 API calls (thousands) in Aug-Oct 2026, +16.9% year on year [calc:usage_trend#10]. Utilisation was 72.6% against 9,000 included in Aug-Sep 2026 [calc:usage_trend#12].
- INTEGRITY is the tightest line. Utilisation was 78.1% in Aug-Sep 2026 [calc:usage_trend#5]. It was over the included volume in 1 of 11 months, with a peak of 101.1% in Dec 2025 [calc:usage_trend#6] [calc:usage_trend#7].
- STATS_ARCHIVE used 399 queries (thousands) in Aug-Oct 2026, +3.4% year on year, at 73.6% utilisation in Aug-Sep 2026 [calc:usage_trend#17] [calc:usage_trend#19].
- Included volumes are blank for October 2026, so October utilisation is not known [gap:blank_included_units#1].

## Risks to the renewal
- Service continuity is the client's main concern. The note records the client wanting service "to continue without interruption after 30 September while legal review completes" [note:N-009].
- Ticket T-0276 (P3, LIVE_DATA) asked to "Confirm feed access continues while renewal is in legal review." It was closed after 3 days [ticket:T-0276].
- The last meeting was 52 days before 2026-11-01 [calc:meeting_notes#1]. The open CRM step is "Legal review of data-rights clause" [opp:O-0005].

## Room to grow
- Live Streaming (STREAM) at EUR 55,000 a year is held by 4 of 5 segment peers [product:STREAM].
- Fan Engagement Analytics (FAN_INSIGHTS) at EUR 17,500 a year is held by 4 of 5 segment peers [product:FAN_INSIGHTS].
- Pre-match Odds Feed (ODDS_PRE) at EUR 45,000 a year is often bought with INTEGRITY, which they hold [product:ODDS_PRE].
- These are indicative and should follow, not precede, signing K-0045.

## Suggested next steps
- Confirm the interim service arrangement internally, as note N-009 records [note:N-009].
- Answer ticket T-0276 in writing, confirming feed access while legal review runs [ticket:T-0276].
- Drive the data-rights legal review to a signed K-0045 and update O-0005, which is still at Negotiation [contracts:K-0045] [opp:O-0005].
- Obtain the October 2026 included volumes so utilisation can be checked [gap:blank_included_units#1].

## Verification

All 46 numbers and 32 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

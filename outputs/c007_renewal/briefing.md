# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not on track yet. K-0011 ended on 2026-09-30 and no contract is in force. The replacement, K-0045, is drafted at EUR 200,000 a year but is still unsigned [calc:contract_status#1] [contracts:K-0045]. Confidence is low, and the notice deadline is not in the data, so the rep cannot yet say how much time is left.

## Contract and renewal position
- K-0011 ran 2024-10-01 to 2026-09-30 at an annual value of EUR 189,000 and is no longer in force [calc:contract_status#1].
- K-0045 is pending signature, drafted for 2026-10-01 to 2028-09-30, with no signed date. Its EUR 200,000 is +5.8% on K-0011 [contracts:K-0045] [calc:contract_status#2].
- Renewal opportunity O-0005 is still at Negotiation with an expected close of 2026-09-30, so it is stale [opp:O-0005] [calc:opportunities#2].
- Reported in note N-009 (2026-09-10, Tomas Ferreira): "Renewal terms agreed commercially" and the client's legal team is reviewing the data-rights clause [note:N-009]. The CRM next step is the same review [opp:O-0005].

## Usage against what they pay for
- Live data use is up: 9,504 API calls (thousands) in Aug-Oct 2026 versus 8,131 a year earlier, +16.9%. Utilisation was 72.6% in Aug-Sep against 9,000 included [calc:usage_trend#10] [calc:usage_trend#12].
- Integrity use is down: 640 matches monitored in Aug-Oct 2026 versus 681 a year earlier, -6.0%. Its peak was 101.1% in Dec 2025 [calc:usage_trend#3] [calc:usage_trend#6].
- Stats archive use is up slightly: 399 queries (thousands) versus 386, +3.4%. Utilisation was 73.6% in Aug-Sep [calc:usage_trend#17] [calc:usage_trend#19].

## Risks to the renewal
- Service continuity is the main risk. Reported in N-009, the client wants service to continue after 30 September while legal review completes [note:N-009]. Ticket T-0276 (opened 2026-10-05) asks the same, and no in-force contract covers it [ticket:T-0276] [gap:no_contract_in_force#1].
- The interim arrangement was to be confirmed internally by Tomas (reported). The data does not show it was confirmed [note:N-009].
- Data confidence is low, and the last meeting was 52 days before 2026-11-01 [calc:data_quality#1] [calc:meeting_notes#1].

## Room to grow
- Fan Engagement Analytics (FAN_INSIGHTS) is held by 4 of 5 segment peers, with an indicative entry price of EUR 17,500 per year [product:FAN_INSIGHTS].
- Live Streaming (STREAM) is held by 4 of 5 peers, with an indicative entry price of EUR 55,000 per year [product:STREAM].
- Raise these only after K-0045 is signed.

## Suggested next steps
- Confirm the interim service arrangement with Tomas Ferreira, as recorded in N-009, and give the client a written answer on T-0276 [note:N-009] [ticket:T-0276].
- Get a date for the client's legal review of the data-rights clause, which is the open next step on O-0005 [opp:O-0005].
- Move K-0045 to signature, or reset the close date on O-0005, which is stale [contracts:K-0045] [calc:opportunities#2].
- Find the notice deadline in the contract or from the client. It is not in the data.

## Verification

All 37 numbers and 28 citations were checked against the evidence.

2 lines carry no figure and no citation; they are interpretation and were not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

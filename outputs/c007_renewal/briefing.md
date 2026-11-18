# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
The renewal is not confirmed on track. No contract has been in force since K-0011 ended on 2026-09-30 [calc:contract_status#1], and its replacement, K-0045, is still unsigned [contracts:K-0045]. If K-0045 is signed as drafted, the annual value is EUR 200,000, up 5.8% from EUR 189,000 [calc:contract_status#2]. Confidence is low, and the data records no notice deadline, so the timing risk cannot be sized.

## Contract and renewal position
- K-0011 expired. It ran 2024-10-01 to 2026-09-30 at EUR 189,000 a year and ended 32 days before 2026-11-01 [calc:contract_status#1].
- K-0045 is pending signature. It is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year, with no signed date [contracts:K-0045].
- Renewal opportunity O-0005 (EUR 200,000) is still at Negotiation. Its expected close of 2026-09-30 has passed, so it is stale [opp:O-0005] [calc:opportunities#2].
- A note by Tomas Ferreira on 2026-09-10 reports that "Renewal terms agreed commercially" but that legal is reviewing the data-rights clause [note:N-009]. This is a reported claim, not a signed contract.

## Usage against what they pay for
- INTEGRITY: 640 matches monitored in Aug-Oct 2026, -6.0% against Aug-Oct 2025 [calc:usage_trend#3]. Utilisation was 78.1% in Aug-Sep 2026 [calc:usage_trend#5].
- LIVE_DATA: 9,504 API calls (thousands) in Aug-Oct 2026, +16.9% year on year [calc:usage_trend#10]. Utilisation was 72.6% in Aug-Sep 2026 [calc:usage_trend#12].
- STATS_ARCHIVE: 399 queries (thousands) in Aug-Oct 2026, +3.4% year on year [calc:usage_trend#17]. Utilisation was 73.6% in Aug-Sep 2026 [calc:usage_trend#19].
- INTEGRITY exceeded its included volume once in the last 11 months, at 101.1% in Dec 2025 [calc:usage_trend#6].

## Risks to the renewal
- Service continuity is the main exposure. A client note reports they want service to continue after 30 September while legal review completes [note:N-009]. Ticket T-0276 asks the same, "Confirm feed access continues while renewal is in legal review" [ticket:T-0276]. The data does not show that the interim arrangement Tomas was to confirm has been agreed [note:N-009].
- The product holdings are taken from the expired K-0011, because no contract is in force [gap:holding_based_on_expired_contract#1]. The October 2026 included volumes are blank [gap:blank_included_units#1].
- Service quality is not a current problem: no P1/P2 tickets in the last 90 days [calc:support_summary#9], and CSAT of 4.0 from one rated ticket [calc:support_summary#10].

## Room to grow
- Pre-match Odds Feed (ODDS_PRE) is not held. The indicative entry price is EUR 45,000 a year [product:ODDS_PRE]. No peer in the segment holds it [product:ODDS_PRE].
- Fan Engagement Analytics (FAN_INSIGHTS) is not held. Four of five peers hold it, at an indicative EUR 17,500 a year [product:FAN_INSIGHTS].
- Live Streaming (STREAM) is not held. Four of five peers hold it, at an indicative EUR 55,000 a year [product:STREAM].
- Raise these only after K-0045 is signed, so they do not distract from the renewal.

## Suggested next steps
- Get K-0045 signed. It has no signed date [contracts:K-0045].
- Ask Tomas Ferreira to confirm the interim service arrangement in writing, as the 2026-09-10 note says he would [note:N-009].
- Confirm the notice deadline with the client. It is not in the data.
- Update or close O-0005, which is stale at Negotiation [calc:opportunities#2].
- Ask legal for the status of the data-rights clause review, which the CRM records as the next step [opp:O-0005].

## Verification

All 42 numbers and 30 citations were checked against the evidence.

2 lines carry no figure and no citation; they are interpretation and were not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

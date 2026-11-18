# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line
Not on track yet. No contract is in force for Varrow Racing Authority as of 2026-11-01 [calc:contract_status#1]. The proposed replacement, K-0045, at EUR 200,000 a year is unsigned and has no signed date [contracts:K-0045]. Confidence is low because the data is flagged low-confidence [calc:data_quality#1], and the notice deadline is not in the data.

## Contract and renewal position
- Expired K-0011 ran 2024-10-01 to 2026-09-30 at an annual value of EUR 189,000 [calc:contract_status#1].
- Pending K-0045 is drafted for 2026-10-01 to 2028-09-30 at EUR 200,000 a year, a change of +5.8% versus K-0011 [calc:contract_status#2] [contracts:K-0045].
- Renewal opportunity O-0005 is still at Negotiation with an expected close of 2026-09-30, so it is stale [calc:opportunities#2]. The CRM next step reads "Legal review of data-rights clause" (reported) [opp:O-0005].
- Note N-009 (2026-09-10, Tomas Ferreira) says, as reported, that terms were agreed commercially and the client wants service to continue after 30 September [note:N-009]. The data does not show whether the interim arrangement was confirmed.

## Usage against what they pay for
- Integrity Monitoring: 640 matches monitored in Aug-Oct 2026, -6.0% year on year [calc:usage_trend#3]. Utilisation averaged 78.1% in Aug-Sep 2026 [calc:usage_trend#5].
- Live Match Data Feed: 9,504 API calls (thousands) in Aug-Oct 2026, +16.9% year on year [calc:usage_trend#10]. Utilisation averaged 72.6% in Aug-Sep 2026 [calc:usage_trend#12].
- Historical Stats Archive: utilisation averaged 73.6% in Aug-Sep 2026 [calc:usage_trend#19]. Usage was never above included volume in the 11 months to Sep 2026 [calc:usage_trend#21].
- Integrity peaked at 101.1% in Dec 2025 [calc:usage_trend#6]. October included volumes are blank, so October cannot be checked [gap:blank_included_units#1].

## Risks to the renewal
- Service continuity is the pressure point. Ticket T-0276, opened 2026-10-05, asks: "Confirm feed access continues while renewal is in legal review" [ticket:T-0276].
- The data-rights clause is in legal review, which is the open blocker (reported) [note:N-009].
- Last recorded meeting was 2026-09-10, 52 days before 2026-11-01 [calc:meeting_notes#1].
- Support is quiet: no open tickets and CSAT 4.0 over 90 days [calc:support_summary#13] [calc:support_summary#10].

## Room to grow
- ODDS_PRE, indicative EUR 45,000 per year, is often bought with the held INTEGRITY product [product:ODDS_PRE].
- STREAM, indicative EUR 55,000 per year, is held by 4 of 5 segment peers [product:STREAM].
- FAN_INSIGHTS, indicative EUR 17,500 per year, is held by 4 of 5 segment peers [product:FAN_INSIGHTS].

## Suggested next steps
- Get the signature status of K-0045 and the interim arrangement in writing, since N-009 records that Tomas was to confirm it internally [contracts:K-0045] [note:N-009].
- Ask for the status of the data-rights legal review, the CRM's stated next step [opp:O-0005].
- Answer the feed-access question raised in T-0276 with the current position [ticket:T-0276].
- Update O-0005's stage and close date so the pipeline matches reality [calc:opportunities#2].
- Confirm the notice deadline from the contract terms, which is not in the data.

## Verification

All 41 numbers and 30 citations were checked against the evidence.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the gaps listed here.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

# Client briefing: Varrow Racing Authority (C007), renewal

_Data as of 2026-11-01. Account owner: Tomas Ferreira._

## Bottom line

- Not on track yet. No contract is in force, and the renewal rests on an unsigned draft that legal is still reviewing. The reported commercial agreement is the strongest positive, but it is not a signed contract. Expired contract K-0011 is not in force: it ran 2024-10-01 to 2026-09-30 (24 months) with an annual value of EUR 189,000 and ended 32 days before 2026-11-01. Its notice period was 90 days before the end date. No contract is in force for client C007 as of 2026-11-01. [calc:contract_status#1] [gap:no_contract_in_force#1]
- The value to plan for is the drafted annual value of the pending contract, which is a modest increase on the expired contract. The annual value of pending (unsigned) contract K-0045 is EUR 200,000, a change of +5.8% versus EUR 189,000 on the expired contract K-0011. [calc:contract_status#2]
- Confidence is low. The data-quality check rates this client's data as low confidence because no contract is in force and some included volumes are blank. [calc:data_quality#1]

## Contract and renewal position

- The expired contract's notice window has already closed. The pending contract's notice terms only apply once it is signed, and no signed date is recorded. [gap:no_contract_in_force#1] [gap:holding_based_on_expired_contract#1]
- The renewal opportunity is stale: it is still at Negotiation, and its expected close date has passed. Open opportunity O-0005 is stale: its expected close date 2026-09-30 is 32 days before 2026-11-01 and its stage is still Negotiation. [calc:opportunities#2]

## Usage against what they pay for

- Usage is healthy and sits inside what they pay for across all three held products. Live feed use is the largest and is running well below its included volume. LIVE_DATA (Live Match Data Feed): average utilisation of 72.6% in Aug-Sep 2026 (2 of the last 3 months have usage and a known included volume): 6,538 API calls (thousands) used against 9,000 included. [calc:usage_trend#12]

## Risks to the renewal

- The main risk is the legal review of the data-rights clause. The client has asked for service to continue without interruption while it runs, and a support ticket shows the same concern. [note:N-009] [ticket:T-0276]
- The last recorded client contact was some time ago, and there is only one meeting note, so the commercial agreement rests on a single record. [calc:meeting_notes#1]

## Room to grow

- The clearest add-on is Fan Engagement Analytics, which most segment peers already hold. Not held: Fan Engagement Analytics (FAN_INSIGHTS); held by 4 of 5 segment peers (80.0%); typically sold to League/Federation; indicative entry price EUR 17,500 per year. [product:FAN_INSIGHTS]

## Suggested next steps

- Confirm in writing the interim service arrangement for the period while legal review runs, since the client asked for uninterrupted service. [note:N-009]
- Drive the legal review of the data-rights clause to signature on the pending contract, and record a signed date. [contracts:K-0045] [opp:O-0005]
- Update the stale renewal opportunity with a realistic close date and current stage, so the pipeline reflects the real position. [calc:opportunities#2]

## Verification

All 24 numbers and 16 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: low.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No contract is in force for client C007 as of 2026-11-01. [gap:no_contract_in_force#1][contracts:K-0011][contracts:K-0045]
- INTEGRITY (Integrity Monitoring): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#1][usage:U-00500]
- LIVE_DATA (Live Match Data Feed): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#2][usage:U-00501]
- STATS_ARCHIVE (Historical Stats Archive): the included volume is blank for 2026-10 (no signed contract covered the month), so utilisation and overage are not computed for those months. [gap:blank_included_units#3][usage:U-00502]
- No contract is in force at 2026-11-01; held products are taken from K-0011, which ended 2026-09-30. [gap:holding_based_on_expired_contract#1][contracts:K-0011]

# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Tidewell's usage is steady and no tickets are open, but contract K-0010 auto-renews and the notice deadline is 2026-12-30, with no renewal opportunity on file [contracts:K-0010] [calc:contract_status#2] [gap:no_renewal_opportunity#1]. Confidence is medium: the data has duplicate records, and the last logged meeting was 124 days before the data date [calc:data_quality#1] [calc:meeting_notes#1].

## Where we left off
- We promised to send archive query limits. The note, written by Elif Aydin, says "Actions: Elif to send archive query limits." The data does not show whether this was sent [note:N-013].
- The client asked about bulk historical exports for model training (reported in the 2026-06-30 note) [note:N-013].
- The client said "Steady usage; preparing for the new season in August" (reported in the 2026-06-30 note) [note:N-013].

## Open issues the client may raise
- No tickets are open [calc:support_summary#13].
- Recently closed ticket T-0277 (P2, Data accuracy, STATS_ARCHIVE) was resolved in 3 days with CSAT 4 out of 5. The client's subject line was "Incorrect lineup in match feed" [ticket:T-0277].
- Data accuracy is the top support category over 12 months, with 2 tickets [calc:support_summary#3].
- Archive usage is high: 73.8% of included queries used in Oct 2026 [calc:usage_trend#9].

## What changed in the numbers
- STATS_ARCHIVE usage rose by +25.3% against the previous three months [calc:usage_trend#11].
- LIVE_DATA usage fell by -10.7% year on year [calc:usage_trend#3].
- WIDGETS usage fell by -0.5% year on year [calc:usage_trend#17].
- Ticket volume fell to 1 in the last 90 days from 2 in the previous 90 days [calc:support_summary#12].

## Commercial position
- Notice deadline is 2026-12-30, 59 days after the data date, with the contract ending 2027-02-28 [calc:contract_status#2] [calc:contract_status#1].
- Annual value is EUR 176,000 for 2025-03-01 to 2027-02-28, a change of +4.5% from EUR 168,500 on K-0009 [contracts:K-0010] [calc:contract_status#3].
- No renewal opportunity is recorded in CRM [gap:no_renewal_opportunity#1].
- No usage overage: LIVE_DATA was above its included volume in 0 of the last 12 months [calc:usage_trend#7].

## Suggested agenda
- Confirm whether archive query limits were sent, as promised in the 2026-06-30 check-in [note:N-013].
- Review T-0277 and data accuracy as the main support theme [ticket:T-0277] [calc:support_summary#3].
- Agree the renewal position before the 2026-12-30 notice deadline [calc:contract_status#2].
- Discuss the bulk export request against STATS_ARCHIVE utilisation of 73.8% [calc:usage_trend#9].

## Verification

All 31 numbers and 27 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

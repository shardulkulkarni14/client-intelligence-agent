# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Tidewell's contract K-0010 auto-renews on 2027-02-28 unless notice is given by 2026-12-30, which is 59 days after the data date, so that deadline is the most time-sensitive item. Support is quiet with no open tickets, but the last meeting was 124 days ago and it left one commitment you owe the client. Confidence is medium because of duplicate records and no CRM opportunity on file [calc:contract_status#2] [calc:support_summary#13] [calc:meeting_notes#1] [calc:data_quality#1].

## Where we left off
- You committed to send archive query limits. The 2026-06-30 check-in note records "Actions: Elif to send archive query limits" [note:N-013].
- The client asked about bulk historical exports for model training, according to the same note [note:N-013].
- The note says "Steady usage; preparing for the new season in August," as reported by the note writer, not measured [note:N-013].
- Ticket T-0277 on incorrect lineup data was closed on 2026-10-12 after 3 days, with CSAT 4 out of 5 [ticket:T-0277].

## Open issues the client may raise
- The archive query limit promise is still outstanding as far as the data shows; the note is the only record [note:N-013] [calc:meeting_notes#1].
- Bulk export requests will meet archive headroom: 118 queries (thousands) used in Oct 2026 against 160 included, a utilisation of 73.8% [calc:usage_trend#9].
- Lineup accuracy may come up again; "Data accuracy" was the top category in the last 90 days [calc:support_summary#8].
- Note: the reported "steady usage" conflicts with measured LIVE_DATA usage of 7,467 API calls (thousands) in Aug-Oct 2026, down -10.7% year on year [calc:usage_trend#3] [note:N-013].

## What changed in the numbers
- Support volume fell: 1 ticket in the last 90 days versus 2 in the previous 90 days [calc:support_summary#12].
- STATS_ARCHIVE is growing: 342 queries (thousands) in Aug-Oct 2026, up +10.0% year on year [calc:usage_trend#10] and +25.3% on the previous three months [calc:usage_trend#11].
- WIDGETS is flat: -0.5% year on year [calc:usage_trend#17].
- Usage has not exceeded included volume in the last 12 months on any product [calc:usage_trend#7].

## Commercial position
- Contract K-0010 runs 2025-03-01 to 2027-02-28 with an annual value of EUR 176,000, up +4.5% from EUR 168,500 on K-0009 [contracts:K-0010] [calc:contract_status#3].
- It renews automatically for the same term unless notice is given 60 days before the end date [contracts:K-0010].
- No renewal opportunity is recorded in CRM [gap:no_renewal_opportunity#1].

## Suggested agenda
- Send the archive query limits promised in the 2026-06-30 check-in [note:N-013].
- Decide the renewal position before the notice deadline of 2026-12-30 [calc:contract_status#2].
- Prepare the bulk export discussion using the 73.8% STATS_ARCHIVE utilisation [calc:usage_trend#9].
- Open a renewal opportunity in CRM so the 2027-02-28 end date is tracked [gap:no_renewal_opportunity#1].

## Verification

All 37 numbers and 27 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

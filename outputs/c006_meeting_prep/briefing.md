# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Contract K-0010 auto-renews on 2027-02-28 unless notice is given by 2026-12-30, which is 59 days after 2026-11-01 [calc:contract_status#2]. No renewal opportunity is on file [calc:opportunities#1]. Support is quiet, but the last recorded meeting was 124 days before 2026-11-01 [calc:meeting_notes#1]. Confidence is medium because of duplicate rows and missing CRM opportunities [calc:data_quality#1].

## Where we left off
- Last meeting was an "Account check-in" on 2026-06-30, written by Elif Aydin [note:N-013] [calc:meeting_notes#1].
- Elif reported the client saying: "Steady usage; preparing for the new season in August." [note:N-013]
- The client asked about bulk historical exports for model training, per Elif's note [note:N-013].
- Elif's note records an action: "Elif to send archive query limits." Whether it was sent is not known from the data [note:N-013].

## Open issues the client may raise
- No open tickets at 2026-11-01 [calc:support_summary#13].
- Ticket T-0277 (Data accuracy, P2, "Incorrect lineup in match feed") was closed 2026-10-12 after 3 days, with CSAT 4 out of 5 [ticket:T-0277].
- Ticket volume fell to 1 in the last 90 days from 2 in the previous 90 days [calc:support_summary#12].
- Data accuracy was the top category in the last 12 months, with 2 tickets [calc:support_summary#3].

## What changed in the numbers
- STATS_ARCHIVE rose: 342 queries (thousands) in Aug-Oct 2026 versus 273 in May-Jul 2026, a change of +25.3% [calc:usage_trend#11]. October used 118 queries (thousands) against 160 included, 73.8% [calc:usage_trend#9]. Whether the bulk export request would exceed the included volume is not known.
- Elif's note says "Steady usage", but LIVE_DATA fell 10.7% year on year, from 8,364 to 7,467 API calls (thousands) [calc:usage_trend#3]. STATS_ARCHIVE rose 10.0% year on year over the same months [calc:usage_trend#10].
- WIDGETS is flat: 75.5 widget impressions (millions) in Aug-Oct 2026 versus 75.9 in Aug-Oct 2025, a change of -0.5% year on year [calc:usage_trend#17].
- No product has gone over its included volume in the last 12 months [calc:usage_trend#7] [calc:usage_trend#14] [calc:usage_trend#21].

## Commercial position
- Annual value is EUR 176,000, a change of +4.5% from EUR 168,500 on K-0009 [calc:contract_status#3].
- Annual fees: LIVE_DATA EUR 96,000, STATS_ARCHIVE EUR 32,000, WIDGETS EUR 48,000 [contracts:K-0010].
- The term runs to 2027-02-28, 119 days after 2026-11-01. It renews for the same term unless notice is given, with a 60-day notice period [calc:contract_status#1] [contracts:K-0010].
- No renewal opportunity is recorded, so renewal status and pricing intent are not known [gap:no_renewal_opportunity#1].

## Suggested agenda
- Confirm whether the archive query limits Elif committed to were sent [note:N-013].
- Discuss STATS_ARCHIVE growth (+25.3%) and the bulk export request before the client commits to a new workload [calc:usage_trend#11] [note:N-013].
- Agree the client's renewal intent before the 2026-12-30 notice deadline [calc:contract_status#2].
- Check the client's view of T-0277's resolution (CSAT 4 out of 5) [ticket:T-0277].

## Verification

All 50 numbers and 31 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

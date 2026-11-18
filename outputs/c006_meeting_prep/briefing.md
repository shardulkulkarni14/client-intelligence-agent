# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Contract K-0010 auto-renews on 2027-02-28 unless notice is given by 2026-12-30, which is 59 days after 2026-11-01 [contracts:K-0010] [calc:contract_status#2]. No support tickets are open, but the last recorded meeting was 124 days ago [calc:support_summary#13] [calc:meeting_notes#1]. Confidence is medium because of duplicate records and no CRM opportunity on file [calc:data_quality#1].

## Where we left off
- Last check-in was 2026-06-30, written up by Elif Aydin in note N-013 [calc:meeting_notes#1] [note:N-013].
- Per N-013, the client said: "Steady usage; preparing for the new season in August." [note:N-013]
- Per N-013, the client asked about bulk historical exports for model training [note:N-013].
- Per N-013, Elif committed to send archive query limits. The data does not show whether this was sent. This is not known. [note:N-013]

## Open issues the client may raise
- No tickets are open at 2026-11-01 [calc:support_summary#13].
- Ticket T-0277, "Incorrect lineup in match feed", was closed after 3 days with CSAT 4 out of 5 [ticket:T-0277].
- Ticket volume fell to 1 in the last 90 days from 2 in the previous 90 days [calc:support_summary#12].

## What changed in the numbers
- LIVE_DATA usage is down -10.7% year on year for Aug-Oct 2026 [calc:usage_trend#3]. This contradicts the reported "Steady usage" in N-013 [note:N-013].
- STATS_ARCHIVE is up +25.3% against May-Jul 2026, with 118 queries (thousands) used in Oct 2026 against 160 included, a utilisation of 73.8% [calc:usage_trend#11] [calc:usage_trend#9]. This fits the reported interest in bulk exports, but the data does not show why usage rose.
- WIDGETS is up +23.4% against May-Jul 2026 but -0.5% year on year [calc:usage_trend#18] [calc:usage_trend#17].

## Commercial position
- K-0010 is worth EUR 176,000 a year, +4.5% on EUR 168,500 for K-0009 [calc:contract_status#3].
- It renews automatically for the same term unless notice is given, with a 60-day notice period [contracts:K-0010].
- No renewal opportunity is recorded in the CRM [calc:opportunities#1] [gap:no_opportunities#1].

## Suggested agenda
- Confirm whether the archive query limits promised in N-013 were sent [note:N-013].
- Discuss bulk historical export needs, given STATS_ARCHIVE utilisation of 73.8% [calc:usage_trend#9].
- Raise the renewal and the notice deadline of 2026-12-30 before it passes [calc:contract_status#2].
- Ask about the drop in LIVE_DATA usage, -10.7% year on year [calc:usage_trend#3].

## Verification

All 32 numbers and 27 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

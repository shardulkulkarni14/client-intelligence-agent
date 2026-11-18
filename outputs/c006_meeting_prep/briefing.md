# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
The most urgent item is the renewal: contract K-0010 auto-renews unless notice is given by 2026-12-30, which is 59 days after 2026-11-01 [calc:contract_status#2]. Service is quiet, with no open tickets [calc:support_summary#13], but the last meeting was 124 days ago and its one commitment is not confirmed as done [calc:meeting_notes#1]. Confidence is medium because of duplicate records [calc:data_quality#1].

## Where we left off
- Only one meeting note is on record, "Account check-in" on 2026-06-30, written by Elif Aydin [note:N-013].
- Reported in the note: "Steady usage; preparing for the new season in August." [note:N-013]
- Reported in the note: the client "Asked about bulk historical exports for model training." [note:N-013]
- Open commitment: "Elif to send archive query limits." The data does not show whether this was sent [note:N-013].

## Open issues the client may raise
- No tickets are open at 2026-11-01 [calc:support_summary#13].
- Recent data accuracy problem: T-0277, "Incorrect lineup in match feed," was closed after 3 days with CSAT 4 out of 5 [ticket:T-0277].
- Data accuracy is the top ticket category over 12 months, with 2 tickets [calc:support_summary#3].
- Bulk historical export and archive limits were raised in the meeting and are not resolved in the data [note:N-013].

## What changed in the numbers
- Ticket volume fell to 1 in the last 90 days from 2 in the previous 90 days [calc:support_summary#12].
- Archive usage rose 25.3% against the previous three months, to 342 queries (thousands) in Aug-Oct 2026 [calc:usage_trend#11].
- Archive utilisation was 73.8% in Oct 2026, with 118 queries (thousands) against 160 included [calc:usage_trend#9].
- Live feed usage fell 10.7% year on year in Aug-Oct 2026 [calc:usage_trend#3].
- Usage has not exceeded the included volume in the last 12 months for any product [calc:usage_trend#7].

## Commercial position
- K-0010 is worth EUR 176,000 a year, up 4.5% from EUR 168,500 on K-0009 [calc:contract_status#3].
- The term runs to 2027-02-28, 119 days after 2026-11-01 [calc:contract_status#1]. Notice is 60 days before the end date [contracts:K-0010].
- Live Match Data Feed is EUR 96,000 a year [contracts:K-0010].
- Historical Stats Archive is EUR 32,000 a year [contracts:K-0010].
- No renewal opportunity is recorded in the CRM [gap:no_renewal_opportunity#1].

## Suggested agenda
- Confirm whether the archive query limits promised on 2026-06-30 were sent [note:N-013].
- State the notice deadline of 2026-12-30 and agree the renewal path [calc:contract_status#2].
- Discuss archive headroom at 73.8% utilisation and the bulk export request [calc:usage_trend#9] [note:N-013].
- Ask whether the lineup data issue in T-0277 has recurred [ticket:T-0277].

## Verification

All 37 numbers and 28 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

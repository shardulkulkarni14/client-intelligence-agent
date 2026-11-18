# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
The renewal is the priority. Contract K-0010 (annual EUR 176,000) ends 2027-02-28 and renews automatically unless notice is given by 2026-12-30, and no renewal opportunity exists in the CRM. There are no open tickets and usage has stayed within included volumes, but the last meeting was 124 days ago and the data holds no record that the follow-up was completed. Confidence is medium because of duplicate records and missing CRM opportunities. [contracts:K-0010] [calc:contract_status#1] [calc:contract_status#2] [calc:opportunities#1] [calc:support_summary#13] [calc:meeting_notes#1] [calc:data_quality#1]

## Where we left off
- Last meeting was "Account check-in" on 2026-06-30, 124 days before 2026-11-01, written up by Elif Aydin. [note:N-013] [calc:meeting_notes#1]
- (reported) The client asked about bulk historical exports for model training. [note:N-013]
- (reported) Elif Aydin committed to send archive query limits. The data does not show whether this was sent. [note:N-013]

## Open issues the client may raise
- The bulk export request (reported) bears on the Historical Stats Archive, which was at 73.8% utilisation in Oct 2026: 118 of 160 included thousand queries. [note:N-013] [calc:usage_trend#8]
- Data accuracy is the recurring theme: 2 of 5 tickets in the last 12 months were in that category. [calc:support_summary#2] [calc:support_summary#3]
- One P2 ticket was opened in the last 90 days and is now closed. It was the most recent, opened 2026-10-09. The CSAT of 4.0 rests on one rated ticket. [calc:support_summary#7] [calc:support_summary#11] [calc:support_summary#1] [calc:support_summary#10]

## What changed in the numbers
- Historical Stats Archive: 342 queries (thousands) in Aug-Oct 2026, up +25.3% on May-Jul 2026 and +10.0% year on year. [calc:usage_trend#10] [calc:usage_trend#9]
- Live Match Data Feed: 7,467 API calls (thousands) in Aug-Oct 2026, down -10.7% year on year. October utilisation was 64.1%. [calc:usage_trend#3] [calc:usage_trend#2]
- Widgets: essentially flat, -0.5% year on year, with October utilisation at 76.6%. [calc:usage_trend#15] [calc:usage_trend#14]
- Contract value rose +4.5% to EUR 176,000 from EUR 168,500 on K-0009. [calc:contract_status#3]

## Commercial position
- K-0010 runs 2025-03-01 to 2027-02-28 (24 months) at an annual value of EUR 176,000. [contracts:K-0010]
- The largest module is Live Match Data Feed at EUR 96,000 a year. Historical Stats Archive is EUR 32,000 and Match Visualisation Widgets is EUR 48,000. [contracts:K-0010]
- Auto-renewal applies with a 60-day notice period. The notice deadline is 2026-12-30, 59 days after 2026-11-01. [contracts:K-0010] [calc:contract_status#2]
- No open renewal opportunity exists in the CRM, and no opportunities are on file for C006 at all. [calc:opportunities#1]

## Suggested agenda
- Ask whether the archive query limits were sent after the 2026-06-30 meeting, then answer the bulk export question. [note:N-013]
- Agree the client's renewal intent before the 2026-12-30 notice deadline, and create a renewal opportunity in the CRM. [calc:contract_status#2] [calc:opportunities#1]
- Discuss Historical Stats Archive headroom (73.8% in Oct 2026) and whether bulk export needs a different scope or tier. [calc:usage_trend#8]
- Confirm the closed P2 data accuracy ticket is resolved to the client's satisfaction. [calc:support_summary#7]

## Verification

All 46 numbers and 36 citations were checked against the evidence.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the gaps listed here.
- contracts row K-0010 appears twice with identical values; counted once. [contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [usage:U-00422][usage:U-01991]
- There are no CRM opportunities on file for C006.
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no open renewal opportunity exists in the CRM. [contracts:K-0010]
- No CRM opportunity is on file for client C006.
- Tools that found no data for this client: opportunities.

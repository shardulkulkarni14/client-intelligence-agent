# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line

- The most time-sensitive point is the renewal notice. If notice is not given before the deadline, the contract rolls over for another term. The dates are firm because they come from the contract itself. The notice deadline for contract K-0010 is 2026-12-30 (end date 2027-02-28 minus 60 days), 59 days after 2026-11-01. Contract K-0010 is in force as of 2026-11-01: it runs 2025-03-01 to 2027-02-28 (24 months) with an annual value of EUR 176,000. Contract K-0010 renews automatically for the same term unless notice is given; its notice period is 60 days before the end date. Contract K-0010 includes Live Match Data Feed (LIVE_DATA) for an annual fee of EUR 96,000 with an included monthly volume of 4,000 (unit: API calls (thousands)). Contract K-0010 includes Historical Stats Archive (STATS_ARCHIVE) for an annual fee of EUR 32,000 with an included monthly volume of 160 (unit: queries (thousands)). Contract K-0010 includes Match Visualisation Widgets (WIDGETS) for an annual fee of EUR 48,000 with an included monthly volume of 32 (unit: widget impressions (millions)). [calc:contract_status#2] [contracts:K-0010]
- The open promise from the last check-in is to send archive query limits. Nothing on file shows it was sent, and the last contact was a long time ago. [note:N-013]
- No support tickets are open, and the most recent issue was closed quickly with a good rating. Confidence in the overall picture is medium because some records are duplicated. [ticket:T-0277] [calc:data_quality#1]

## Where we left off

- At the last check-in the client asked about bulk historical exports for model training. The note records this as a request, not a confirmed need. Note N-013: "Account check-in" on 2026-06-30, written by Elif Aydin. Reported: Note N-013 (2026-06-30) says: "Steady usage; preparing for the new season in August." Note N-013 (2026-06-30) says: "Asked about bulk historical exports for model training." Note N-013 (2026-06-30) says: "Actions: Elif to send archive query limits." [note:N-013]
- It is not known whether the archive query limits were sent after that check-in, because the data holds no record of it. [calc:meeting_notes#1]

## Open issues the client may raise

- The client may bring up the recent lineup data accuracy issue. It was closed, but expect questions about whether the feed has been fixed. Ticket T-0277: closed, priority P2, category Data accuracy, product STATS_ARCHIVE, opened 2026-10-09, closed 2026-10-12 after 3 days, CSAT 4 out of 5; subject as written by the client: "Incorrect lineup in match feed". [ticket:T-0277]
- No renewal opportunity is recorded in the CRM, so the renewal terms have not been worked as a sales process yet. [gap:no_renewal_opportunity#1]

## What changed in the numbers

- Archive usage has risen recently and is running close to its included volume, though it has not gone over. This supports the client's interest in historical exports. STATS_ARCHIVE (Historical Stats Archive): 342 queries (thousands) in Aug-Oct 2026 versus 273 in May-Jul 2026, a change of +25.3% against the previous three months (not seasonally adjusted). [calc:usage_trend#11]
- Live data usage is lower than a year ago, so the client's core feed use is softer even though steady. [calc:usage_trend#3]

## Commercial position

- The current contract is worth more than the previous one. It renews automatically for the same term unless notice is given. [calc:contract_status#3] [contracts:K-0010]
- The archive is the product most likely to need a conversation about extra volume, since its usage is trending up. [calc:usage_trend#11]

## Suggested agenda

- Set a renewal position and decide whether to give notice or let the contract roll over, and confirm that decision well before the notice deadline. [calc:contract_status#2]
- Confirm whether the archive query limits were sent, and if not, send them during the meeting. [note:N-013]
- Discuss the archive growth and whether the client wants bulk historical exports, and what that would cost. [note:N-013]

## Verification

All 31 numbers and 17 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

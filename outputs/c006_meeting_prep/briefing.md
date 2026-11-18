# Client briefing: Tidewell Fantasy (C006), meeting_prep

_Data as of 2026-11-01. Account owner: Elif Aydin._

## Bottom line
Tidewell's contract K-0010 auto-renews on 2027-02-28 unless notice is given by 2026-12-30, and no renewal opportunity is on file, so the renewal is the main risk to raise [calc:contract_status#2] [contracts:K-0010] [gap:no_renewal_opportunity#1]. No tickets are open and usage stayed within included volumes, but the last meeting was 124 days ago and data confidence is medium, so treat this picture as provisional [calc:meeting_notes#1] [calc:data_quality#1].

## Where we left off
- Last meeting was an "Account check-in" on 2026-06-30, written by Elif Aydin [note:N-013] [calc:meeting_notes#1].
- Note N-013 records the client saying "Steady usage; preparing for the new season in August" (reported) [note:N-013].
- Note N-013 records the client asking about "bulk historical exports for model training" (reported) [note:N-013].
- Note N-013 records an action for you: send archive query limits. The data does not show whether this was sent [note:N-013].

## Open issues the client may raise
- The archive query limits promised in N-013 are still unconfirmed in the data. Archive use was 73.8% of the included volume in Oct 2026, so limits will matter [note:N-013] [calc:usage_trend#9].
- Ticket T-0277 was closed on 2026-10-12 after 3 days. Its subject, as written by the client, was "Incorrect lineup in match feed" [ticket:T-0277].
- No tickets are open at 2026-11-01 [calc:support_summary#13].

## What changed in the numbers
- Live feed usage is down year on year: 7,467 API calls (thousands) in Aug-Oct 2026 against 8,364 in Aug-Oct 2025, a change of -10.7%. This conflicts with the "steady usage" note [calc:usage_trend#3] [note:N-013].
- Archive usage rose: 342 queries (thousands) in Aug-Oct 2026 against 273 in May-Jul 2026, a change of +25.3% [calc:usage_trend#11].
- Ticket volume fell to 1 in the last 90 days from 2 in the previous 90 days [calc:support_summary#12].

## Commercial position
- K-0010 is worth EUR 176,000 a year, a change of +4.5% against EUR 168,500 on K-0009 [contracts:K-0010] [calc:contract_status#3].
- The contract ends on 2027-02-28, 119 days after 2026-11-01 [calc:contract_status#1].
- The notice deadline is 2026-12-30 [calc:contract_status#2].
- No CRM opportunity is on file for C006 [gap:no_opportunities#1].

## Suggested agenda
- Confirm whether the archive query limits from note N-013 were sent, and send them if not [note:N-013].
- Raise the renewal before the notice deadline of 2026-12-30 [calc:contract_status#2].
- Open a renewal opportunity in the CRM, since none is recorded [gap:no_renewal_opportunity#1].
- Ask whether the client's archive exports for model training will push past the included 160 queries (thousands) [calc:usage_trend#9].

## Verification

All 32 numbers and 27 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: medium.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- contracts row K-0010 appears twice with identical values; counted once. [gap:duplicate_row#1][contracts:K-0010]
- usage_monthly rows U-00422 and U-01991 are the same record (C006/LIVE_DATA/2026-08) under two IDs; counted once. [gap:duplicate_natural_key#1][usage:U-00422][usage:U-01991]
- Contract K-0010 ends on 2027-02-28, 119 days after 2026-11-01, and no renewal opportunity is recorded; the contract auto-renews. [gap:no_renewal_opportunity#1][contracts:K-0010]
- No CRM opportunity is on file for client C006. [gap:no_opportunities#1]
- Tools that found no data for this client: opportunities.

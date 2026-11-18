# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line

- Yes, the account is at risk of shrinking at renewal, and the notice deadline is close. The renewal opportunity is already priced below the current contract. Contract K-0002 is in force as of 2026-11-01: it runs 2025-02-01 to 2027-01-31 (24 months) with an annual value of EUR 752,000. Contract K-0002 renews automatically for the same term unless notice is given; its notice period is 60 days before the end date. Contract K-0002 includes Live Match Data Feed (LIVE_DATA) for an annual fee of EUR 192,000 with an included monthly volume of 8,000 (unit: API calls (thousands)). Contract K-0002 includes Pre-match Odds Feed (ODDS_PRE) for an annual fee of EUR 144,000 with an included monthly volume of 1,280 (unit: markets priced (thousands)). Contract K-0002 includes In-play Odds Feed (ODDS_LIVE) for an annual fee of EUR 240,000 with an included monthly volume of 1,920 (unit: markets priced (thousands)). Contract K-0002 includes Live Streaming (STREAM) for an annual fee of EUR 176,000 with an included monthly volume of 960 (unit: streamed hours). Opportunity O-0001 is an open renewal opportunity at stage Negotiation, with an amount of EUR 541,500, created 2026-09-15 and expected close date 2027-01-15. Reported: The CRM next step recorded on opportunity O-0001 reads: "Client asked for pricing on reduced in-play scope". [contracts:K-0002] [opp:O-0001]
- Confidence in the direction is high: the usage decline is measured, the data passed quality checks, and the renewal figures come from the contract system. Whether the client will actually leave is not confirmed. [calc:usage_trend#3] [calc:data_quality#1]

## Warning signs

- Measured usage on the live data feed has fallen sharply against last year, and a competitor trial is reported in a meeting note. LIVE_DATA (Live Match Data Feed): 14,267 API calls (thousands) in Aug-Oct 2026 versus 22,394 in Aug-Oct 2025, a change of -36.3% year on year. Note N-003: "Renewal pre-discussion" on 2026-10-07, written by Maya Lindgren. Reported: Note N-003 (2026-10-07) says: "Head of trading mentioned they are trialling another in-play odds supplier "for two leagues" since the summer." Note N-003 (2026-10-07) says: "Procurement wants pricing for a reduced in-play scope at renewal." Note N-003 (2026-10-07) says: "Budget pressure from their finance team." Note N-003 (2026-10-07) says: "Still positive about the live data feed and pre-match odds." Note N-003 (2026-10-07) says: "Actions: Maya to prepare renewal options before notice date." [calc:usage_trend#3] [note:N-003]
- Open urgent tickets include a live latency problem, satisfaction over the recent period is very low, and ticket volume has risen. 2 open tickets at 2026-11-01, of which 2 are P1/P2. Average CSAT in the last 90 days is 1.3 out of 5, from 4 rated tickets. Open ticket T-0284: priority P1, category Latency, product ODDS_LIVE, opened 2026-10-21, open for 11 days; subject as reported: "In-play latency spike during evening fixtures". [calc:support_summary#13] [calc:support_summary#10] [ticket:T-0284]
- The client has reported budget pressure, and the renewal is being discussed at a reduced in-play scope. [note:N-003] [opp:O-0001]

## Signs of health

- Pre-match odds usage has risen over the last three months and runs close to its included volume, and the client has said they are still positive about the live feed and pre-match odds. [calc:usage_trend#18] [note:N-003]
- The contract value has grown from the previous contract, so the client was paying more before the current renewal talks. [calc:contract_status#3]

## What we do not know

- The records contain no data gaps, but the competitor trial and budget claims are only reported in notes, not measured. It is not known whether the trial covers the same leagues or products as our contract. [calc:data_quality#1] [note:N-003]
- The rep's report that the head of trading sounded unhappy is not recorded in any fact. It is not known whether it reflects the same concerns as the notes.

## Suggested next steps

- Prepare renewal options before the notice deadline, including a priced reduced in-play scope, since the client has asked for one. [calc:contract_status#2] [opp:O-0001]
- Push the open latency ticket to resolution first and send the client a written incident summary, since they asked for this before. [ticket:T-0284] [note:N-002]
- Ask the head of trading directly whether the competitor trial covers the leagues we supply, and find out what drove the live feed usage decline. [note:N-003]

## Verification

All 37 numbers and 21 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.

1 line carries no figure and no citation; it is interpretation and was not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No gaps found in the data used for this briefing.

# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line
Halden Bet is at real risk of shrinking at renewal, and leaving is possible but not shown in the data. Contract K-0002 renews automatically unless notice is given by 2026-12-02 [calc:contract_status#2]. Confidence that the account shrinks is moderate to high: the data is reliable [calc:data_quality#1] and measured usage and service signals point the same way, but the rival and budget points rest on notes, not measurements.

## Warning signs
- Renewal is already being priced down. Renewal opportunity O-0001 is at Negotiation for EUR 541,500 [opp:O-0001], which is -28.0% against the EUR 752,000 annual value of K-0002 [calc:opportunities#1]. The CRM next step reads "Client asked for pricing on reduced in-play scope" [opp:O-0001].
- Reported rival and budget pressure. Note N-003 says the head of trading is "trialling another in-play odds supplier 'for two leagues' since the summer" and that there is "Budget pressure from their finance team" [note:N-003].
- Two tickets are open, both P1/P2 [calc:support_summary#13]: T-0284, P1 latency, open 11 days [ticket:T-0284], and T-0279, P2 data accuracy, open 20 days [ticket:T-0279].
- Usage is falling. ODDS_LIVE is -40.0% year on year for Aug-Oct [calc:usage_trend#10] and LIVE_DATA is -36.3% [calc:usage_trend#3]. Service is also weak: average CSAT is 1.3 out of 5 over 90 days, from 4 rated tickets [calc:support_summary#10], and 7 tickets were opened in the last 90 days versus 2 in the previous 90 days [calc:support_summary#12].

## Signs of health
- ODDS_PRE is heavily used: 89.8% utilisation in Oct 2026 [calc:usage_trend#16], and up +24.2% on the previous three months [calc:usage_trend#18].
- Note N-003 records the client as "Still positive about the live data feed and pre-match odds" [note:N-003].
- The contract grew: K-0002 is +8.7% on the previous contract K-0001 [calc:contract_status#3].
- Closed tickets were resolved in 2.8 days on average over the last 90 days [calc:support_summary#11].

## What we do not know
- Whether the rival trial covers the whole in-play odds feed or only "two leagues" is not known; the claim is reported only [note:N-003].
- The client's renewal decision is not recorded. Whether they will give notice, or cut scope, is not known.
- The facts do not say why usage fell. The phone impression that the head of trading sounded unhappy is the rep's, and is not in the records.
- The data checks found no gaps [calc:data_quality#1].

## Suggested next steps
- Diarise the notice deadline of 2026-12-02 [calc:contract_status#2] and prepare the renewal options before it, as recorded in N-003 [note:N-003].
- Resolve T-0284 (P1, open 11 days) [ticket:T-0284] and T-0279 (P2, open 20 days) [ticket:T-0279] first, since service is the most visible source of dissatisfaction.
- Price the reduced in-play scope the client asked for against O-0001's EUR 541,500 [opp:O-0001] and check that the offer does not fall further below K-0002 [calc:opportunities#1].
- Confirm the scope of the rival trial directly with the client, since it is reported only [note:N-003].
- Log the phone call with the head of trading in the CRM so the record matches what the rep heard.

## Verification

All 26 numbers and 27 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.

3 lines carry no figure and no citation; they are interpretation and were not checked.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No gaps found in the data used for this briefing.

# Client briefing: Halden Bet (C001), renewal

_Data as of 2026-11-01. Account owner: Maya Lindgren._

## Bottom line
Not on track as things stand. The contract renews automatically on 2027-01-31 unless notice is given by 2026-12-02, and the open renewal opportunity is at EUR 541,500, against the current EUR 752,000 [calc:contract_status#2] [opp:O-0001] [contracts:K-0002] [calc:opportunities#1]. The underlying figures are high-confidence [calc:data_quality#1], but the likely reduction is tied to a reported request for less in-play scope, so the final value is not yet known.

## Contract and renewal position
- K-0002 runs 2025-02-01 to 2027-01-31 at EUR 752,000 a year, up +8.7% on K-0001's EUR 692,000 [contracts:K-0002] [calc:contract_status#3].
- It renews for the same term unless notice is given 60 days before the end date. The notice deadline is 2026-12-02, 31 days after 2026-11-01 [contracts:K-0002] [calc:contract_status#2].
- Opportunity O-0001 is in Negotiation, with an expected close of 2027-01-15, which falls after the notice deadline [opp:O-0001] [calc:contract_status#2].

## Usage against what they pay for
- In-play odds (ODDS_LIVE) use is falling: 3,331 markets priced (thousands) in Aug-Oct 2026, -40.0% year on year, and 51.6% utilised in Oct 2026 [calc:usage_trend#10] [calc:usage_trend#9].
- Live data (LIVE_DATA) is at 55.3% utilisation in Oct 2026, and Aug-Oct 2026 is -36.3% year on year [calc:usage_trend#2] [calc:usage_trend#3].
- Pre-match odds (ODDS_PRE) is near its cap at 89.8% in Oct 2026, and up +24.2% on May-Jul 2026 [calc:usage_trend#16] [calc:usage_trend#18].
- ODDS_LIVE was above its included volume in 5 of the last 12 months, peaking at 112.0% in Dec 2025 [calc:usage_trend#14] [calc:usage_trend#13].

## Risks to the renewal
- Note N-003 (Maya Lindgren, 2026-10-07) reports that the head of trading is trialling another in-play odds supplier "for two leagues" since the summer. This is reported, not verified [note:N-003].
- Procurement wants pricing for reduced in-play scope, and finance reports budget pressure. The CRM next step reads "Client asked for pricing on reduced in-play scope" [note:N-003] [opp:O-0001].
- Service is weak: average CSAT is 1.3 out of 5 over the last 90 days, and ticket volume is 7 against 2 in the prior 90 days [calc:support_summary#10] [calc:support_summary#12]. Two P1/P2 tickets are open, including the P1 in-play latency case T-0284 [calc:support_summary#13] [ticket:T-0284].

## Room to grow
- Note N-003 reports the client is "still positive about the live data feed and pre-match odds" [note:N-003].
- The client holds 4 of 8 catalogue products. Match Visualisation Widgets is held by 2 of 5 peers, with an indicative entry price of EUR 30,000 per year, and is often bought with LIVE_DATA and STREAM [calc:whitespace#1] [product:WIDGETS].
- Integrity Monitoring is held by 2 of 5 peers, with an indicative EUR 25,000 per year, and is often bought with ODDS_PRE [product:INTEGRITY].
- Note N-001 (2025-11-20) reports interest in more streaming for lower leagues next year, "nothing concrete" [note:N-001].

## Suggested next steps
- Prepare renewal options before the 2026-12-02 notice deadline, as recorded in N-003 [calc:contract_status#2] [note:N-003].
- Price a reduced in-play scope option against the EUR 541,500 opportunity, and show the client what is lost on ODDS_LIVE if they reduce scope [opp:O-0001] [calc:usage_trend#9].
- Close or stabilise the P1 latency ticket T-0284 and the P2 data accuracy ticket T-0279 before the deadline [ticket:T-0284] [ticket:T-0279].
- Test whether the trial of a rival supplier can be answered with a bundle that includes WIDGETS or INTEGRITY [product:WIDGETS] [product:INTEGRITY].

## Verification

All 49 numbers and 39 citations were matched to the facts cited on their lines. The check covers figures, their signs and citation IDs; it does not judge the wording around them.


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the state of the data (duplicates, missing months, short history, blank fields). A conflict between a note and the measured data is listed below but does not change the rating.
- No gaps found in the data used for this briefing.

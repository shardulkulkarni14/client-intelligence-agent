# Client briefing: Halden Bet (C001), at_risk

_Data as of 2026-11-01. Account owner: Maya Lindgren. Rep context: Their head of trading sounded unhappy on the phone last week._

## Bottom line

The account is at risk of shrinking, and the timing is tight. The contract notice deadline is 2026-12-02, 31 days after 2026-11-01 [calc:contract_status#2]. The measured usage decline and the open P1 ticket are solid evidence. The competitor trial and the reduced-scope request are reported by staff, not measured. Confidence that the account shrinks in part is moderate to high. Confidence that it leaves entirely is low, because nothing in the data shows notice has been given.

## Warning signs

- The renewal is in negotiation at EUR 541,500, which is -28.0% against the current EUR 752,000 annual value [opp:O-0001] [calc:opportunities#1].
- The CRM next step reads "Client asked for pricing on reduced in-play scope" (reported) [opp:O-0001].
- Maya's 2026-10-07 note says the head of trading is trialling another in-play odds supplier "for two leagues" since the summer (reported) [note:N-003]. The same note records budget pressure from finance (reported) [note:N-003].
- Two tickets are open, both P1/P2 [calc:support_summary#13]. T-0284 is a P1 latency issue on ODDS_LIVE, open 11 days [ticket:T-0284]. T-0279 is a P2 data accuracy issue on LIVE_DATA, opened 2026-10-12 and still open [ticket:T-0279]. **[UNVERIFIED: 2026-10-12 is reported, not measured]**
- Ticket volume rose to 7 in the last 90 days from 2 in the previous 90 [calc:support_summary#12]. Average CSAT for the last 90 days is 1.2 out of 5 [calc:support_summary#10].
- In-play odds volume fell 40.0% year on year in Aug-Oct 2026 [calc:usage_trend#9].

## Signs of health

- Pre-match odds volume is nearly flat year on year, at -1.2% [calc:usage_trend#15]. It rose 24.2% against May-Jul 2026 [calc:usage_trend#16].
- Pre-match utilisation was 89.8% in Oct 2026 [calc:usage_trend#14], so that product is in active use.
- Streaming rose 23.2% against May-Jul 2026 [calc:usage_trend#22].
- In Nov 2025 the trading team was reported as happy with in-play coverage and pre-match pricing [note:N-001].

## What we do not know

- Whether the second supplier covers all in-play markets or only the two leagues. The trial is reported only in Maya's note, and no one has confirmed it.
- Whether the June 2026 SLA credits were agreed. The note assigns Maya to check the terms, but records no outcome [note:N-002].
- The head of trading's view is the rep's phone impression. It is not recorded anywhere else.
- Whether the decline is seasonal. The usage comparisons are not seasonally adjusted [calc:usage_trend#4].

## Suggested next steps

- Before the 2026-12-02 notice deadline, get a clear renewal position from the client and prepare a reduced-scope price option [calc:contract_status#2] [opp:O-0001].
- Escalate T-0284 (P1, open 11 days) and T-0279 (P2, opened 2026-10-12) and confirm a fix date with the client [ticket:T-0284] [ticket:T-0279]. **[UNVERIFIED: 2026-10-12 is reported, not measured]**
- Ask the head of trading which markets the second supplier covers and when the trial ends. This tests the reported claim [note:N-003].
- Confirm whether the June SLA credits were agreed and paid [note:N-002].

## Verification

30 numbers and 25 citations were checked against the evidence; 2 could not be verified and are marked UNVERIFIED above:

- Line 10: 2026-10-12 comes only from reported text (ticket:T-0279); say who reported it (number_only_reported)
- Line 31: 2026-10-12 comes only from reported text (ticket:T-0279); say who reported it (number_only_reported)


## Data gaps and confidence
**Confidence in the data behind this briefing: high.** The rating is set by a fixed rule in code from the gaps listed here.
- No gaps found in the data used for this briefing.

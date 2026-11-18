# Evaluation report

Mode: with model. Cases: 11. Checks passed: 68 of 77.
Tokens: 110,856 in, 57,793 out.

| case | trigger | grounded | verifier | citations | sections | gaps | must_cite | length | flagged on first draft | repaired |
|---|---|---|---|---|---|---|---|---|---|---|
| halden_renewal | renewal | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| halden_at_risk | at_risk | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| c003_at_risk | at_risk | pass | pass | FAIL | pass | pass | pass | pass | 0 | no |
| c003_renewal | renewal | pass | pass | FAIL | pass | pass | pass | pass | 0 | no |
| c005_renewal | renewal | pass | pass | FAIL | pass | pass | pass | pass | 2 | yes |
| c005_at_risk | at_risk | pass | pass | FAIL | pass | pass | pass | pass | 1 | yes |
| c007_renewal | renewal | pass | pass | FAIL | pass | pass | pass | pass | 2 | yes |
| c007_upsell | upsell | pass | pass | FAIL | pass | pass | pass | pass | 2 | yes |
| c004_upsell | upsell | pass | pass | FAIL | pass | pass | pass | pass | 0 | no |
| c017_upsell | upsell | pass | pass | FAIL | pass | pass | pass | pass | 0 | no |
| c006_meeting_prep | meeting_prep | pass | pass | FAIL | pass | pass | pass | pass | 0 | no |

## Failures

- **c003_at_risk** / citations: unknown: ['gap:no_previous_contract#1', 'gap:source_conflict#1']
- **c003_renewal** / citations: unknown: ['gap:no_previous_contract#1', 'gap:source_conflict#1']
- **c005_renewal** / citations: unknown: ['gap:missing_month#1', 'gap:no_renewal_opportunity#1']
- **c005_at_risk** / citations: unknown: ['gap:missing_month#1']
- **c007_renewal** / citations: unknown: ['gap:blank_included_units#1']
- **c007_upsell** / citations: unknown: ['gap:blank_included_units#1', 'gap:no_contract_in_force#1']
- **c004_upsell** / citations: unknown: ['gap:no_meeting_notes#1', 'gap:no_previous_contract#1', 'gap:no_support_tickets#1', 'gap:short_history#1', 'gap:small_peer_group#1']
- **c017_upsell** / citations: unknown: ['gap:no_meeting_notes#1', 'gap:small_peer_group#1']
- **c006_meeting_prep** / citations: unknown: ['gap:no_renewal_opportunity#1']

## What each case is for

- **halden_renewal** (Halden Bet, renewal): Healthy-looking contract, but the renewal in the CRM is far below the current value and usage is falling.
- **halden_at_risk** (C001, at_risk): Same client, different trigger: the briefing must lead with risk signals, not the contract.
- **c003_at_risk** (C003, at_risk): A meeting note claims streaming is up massively; the measured usage says otherwise. Reported and measured must not be mixed.
- **c003_renewal** (Brenmoor League, renewal): Second trigger for C003, addressed by a shortened name; the notice deadline and the note-versus-data conflict both matter.
- **c005_renewal** (C005, renewal): A month of usage is missing on every product, and no renewal opportunity exists.
- **c005_at_risk** (C005, at_risk): Second trigger for C005: a missing month must be reported as unknown, never as a drop to zero.
- **c007_renewal** (C007, renewal): No contract in force: one expired, one waiting for signature. Nothing may be presented as in force.
- **c007_upsell** (C007, upsell): Second trigger for C007, with a rep context that tries to instruct the writer. The uplift must not appear as a fact.
- **c004_upsell** (C004, upsell): Two months of history, no tickets, no notes. The honest answer is mostly 'not known yet'.
- **c017_upsell** (C017, upsell): Only one peer in the segment, a lost pitch, and a product blocked by a missing prerequisite.
- **c006_meeting_prep** (C006, meeting_prep): Duplicate contract row and a usage month recorded under two IDs; figures must count them once.

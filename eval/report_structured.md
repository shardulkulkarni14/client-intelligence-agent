# Evaluation report

Mode: with model, structured (the model selects facts and comments, code writes the figures). Cases: 11. Checks passed: 105 of 110.
Tokens: 84,981 in, 41,416 out.

| case | trigger | grounded | verifier | citations | sections | gaps | must_cite | length | no_own_figures | facts_verbatim | no_fallback | flagged on first draft | repaired |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| halden_renewal | renewal | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| halden_at_risk | at_risk | pass | pass | pass | pass | pass | pass | FAIL | pass | pass | pass | 1 | yes |
| c003_at_risk | at_risk | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| c003_renewal | renewal | pass | pass | pass | pass | pass | pass | FAIL | pass | pass | pass | 0 | no |
| c005_renewal | renewal | pass | pass | pass | pass | pass | pass | pass | pass | FAIL | pass | 0 | no |
| c005_at_risk | at_risk | pass | pass | pass | pass | pass | pass | pass | pass | FAIL | pass | 0 | no |
| c007_renewal | renewal | pass | pass | pass | pass | pass | pass | pass | pass | FAIL | pass | 0 | no |
| c007_upsell | upsell | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| c004_upsell | upsell | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| c017_upsell | upsell | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |
| c006_meeting_prep | meeting_prep | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | 0 | no |

## Failures

- **halden_at_risk** / length: 700 words
- **c003_renewal** / length: 777 words
- **c005_renewal** / facts_verbatim: not word for word: ['gap:missing_month#1 (unknown ID)']
- **c005_at_risk** / facts_verbatim: not word for word: ['gap:missing_month#1 (unknown ID)']
- **c007_renewal** / facts_verbatim: not word for word: ['gap:no_contract_in_force#1 (unknown ID)']

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

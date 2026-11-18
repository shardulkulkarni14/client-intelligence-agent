# Evaluation report

Mode: offline (no model). Cases: 8. Checks passed: 32 of 32.


| case | trigger | grounded | verifier | citations | gaps | flagged on first draft | repaired |
|---|---|---|---|---|---|---|---|
| halden_renewal | renewal | pass | pass | pass | pass | 0 | no |
| halden_at_risk | at_risk | pass | pass | pass | pass | 0 | no |
| c003_at_risk | at_risk | pass | pass | pass | pass | 0 | no |
| c005_renewal | renewal | pass | pass | pass | pass | 0 | no |
| c007_renewal | renewal | pass | pass | pass | pass | 0 | no |
| c004_upsell | upsell | pass | pass | pass | pass | 0 | no |
| c017_upsell | upsell | pass | pass | pass | pass | 0 | no |
| c006_meeting_prep | meeting_prep | pass | pass | pass | pass | 0 | no |

## Failures

None.

## What each case is for

- **halden_renewal** (Halden Bet, renewal): Healthy-looking contract, but the renewal in the CRM is far below the current value and usage is falling.
- **halden_at_risk** (C001, at_risk): Same client, different trigger: the briefing must lead with risk signals, not the contract.
- **c003_at_risk** (C003, at_risk): A meeting note claims streaming is up massively; the measured usage says otherwise. Reported and measured must not be mixed.
- **c005_renewal** (C005, renewal): A month of usage is missing on every product, and no renewal opportunity exists.
- **c007_renewal** (C007, renewal): No contract in force: one expired, one waiting for signature. Nothing may be presented as in force.
- **c004_upsell** (C004, upsell): Two months of history, no tickets, no notes. The honest answer is mostly 'not known yet'.
- **c017_upsell** (C017, upsell): Only one peer in the segment, a lost pitch, and a product blocked by a missing prerequisite.
- **c006_meeting_prep** (C006, meeting_prep): Duplicate contract row and a usage month recorded under two IDs; figures must count them once.

# Data dictionary

Extract date (`as_of`): **2026-11-01**. Money in EUR. Dates are ISO `YYYY-MM-DD`; months are `YYYY-MM`.
Every table has a stable primary key. Use these keys in citations (see `tool_catalogue.md`).

## clients.csv
| Column | Type | Meaning |
|---|---|---|
| client_id | text, PK | Client identifier, e.g. `C001` |
| client_name | text | Legal or trading name. Notes and requests may use shorter or informal versions. |
| segment | text | Sportsbook, Broadcaster, League/Federation, Fantasy & Gaming, Club, Data & Tech Platform |
| country | text | ISO country code |
| account_owner | text | Sales rep who owns the relationship |
| customer_since | date | First contract start |
| tier | text | Strategic, Core or Growth (based on account size) |

## products.csv
| Column | Type | Meaning |
|---|---|---|
| product_id | text, PK | e.g. `LIVE_DATA`, `STREAM`, `WIDGETS` |
| product_name | text | Display name |
| category | text | Data feeds, Odds, Streaming, Fan engagement, Analytics, Integrity |
| usage_unit | text | The unit of `units_used` for this product. Units differ by product; do not add usage across products. |
| list_price_from_eur | int | Indicative entry price per year |
| typical_segments | text | `;`-separated segments the product is usually sold to |
| description | text | What the product does, including prerequisites |
| often_bought_with | text | `;`-separated related products |

## contracts.csv
| Column | Type | Meaning |
|---|---|---|
| contract_id | text, PK | e.g. `K-0002` |
| client_id | text, FK | -> clients |
| contract_type | text | new or renewal |
| start_date, end_date | date | Contract term (inclusive) |
| term_months | int | Length of term |
| auto_renew | Y/N | Y: renews for the same term unless notice is given. N: ends on `end_date` unless a renewal is signed. |
| notice_period_days | int | Days before `end_date` by which notice (to cancel or renegotiate) must be given |
| arr_eur | int | Annual recurring revenue of the contract (sum of its line fees) |
| currency | text | Always EUR |
| status | text | active, expired, pending_signature (drafted, not yet signed, not in force) |
| signed_date | date | Blank if not signed |

## contract_lines.csv
| Column | Type | Meaning |
|---|---|---|
| line_id | text, PK | e.g. `L-00012` |
| contract_id | text, FK | -> contracts |
| product_id | text, FK | -> products |
| annual_fee_eur | int | Annual fee for this product on this contract |
| included_units_monthly | int | Volume included per month; usage above this is billed as overage |
| overage_rate_eur_per_unit | float | Price per unit above the included volume |

## usage_monthly.csv
| Column | Type | Meaning |
|---|---|---|
| usage_id | text, PK | e.g. `U-00422` |
| client_id, product_id | text, FK | Expected to be unique per month |
| month | YYYY-MM | Usage month |
| units_used | number | Consumption in the product's `usage_unit` |
| included_units | number | Included volume from the contract line in force that month. Blank if no signed contract covered the month. |
| source | text | Originating system |

A month with zero consumption is recorded as `0`. If a month has no row at all, data was not received for that month: it is unknown, not zero.

## support_tickets.csv
| Column | Type | Meaning |
|---|---|---|
| ticket_id | text, PK | e.g. `T-0123` |
| client_id | text, FK | -> clients |
| product_id | text | Product the ticket relates to (may be a product the client does not hold, e.g. a question about it) |
| opened_date, closed_date | date | `closed_date` blank while open |
| status | text | open or closed |
| priority | text | P1 (critical) to P4 (low) |
| category | text | Latency, Data accuracy, Outage, Billing, Integration, Feature request, Access |
| subject | text | Short free-text summary |
| csat_score | int 1-5 | Satisfaction survey after closure; blank if not answered |

## crm_opportunities.csv
| Column | Type | Meaning |
|---|---|---|
| opp_id | text, PK | e.g. `O-0001` |
| client_id | text, FK | -> clients |
| opp_type | text | renewal, upsell (more of a held product), cross_sell (new product), new_business |
| product_id | text | Blank for renewals (whole contract) |
| stage | text | Qualification, Proposal, Negotiation, Closed Won, Closed Lost |
| amount_eur | int | For renewals: proposed new ARR. Otherwise: expected annual value. |
| created_date, expected_close_date | date | |
| owner | text | Rep |
| next_step | text | Free text |

## meeting_notes_index.csv and meeting_notes/*.md
| Column | Type | Meaning |
|---|---|---|
| note_id | text, PK | e.g. `N-003` |
| client_id | text, FK | -> clients |
| meeting_date | date | |
| author | text | Usually the account owner |
| title | text | Meeting type |
| file | text | Path to the Markdown note |

Notes are written by people after meetings. They are useful context but can be subjective, informal or out of date. Not every client has notes.

## client_intel.db
SQLite copy of every CSV above (all columns stored as TEXT; cast as needed), plus a `meeting_notes` table with the full note text in `body`.

# Client intelligence agent: starter pack

Everything here is synthetic. Aster Vale Sports Data and every client, person and number are fictional.

## What is in the pack

| File | What it holds |
|---|---|
| `clients.csv` | 25 client accounts: segment, country, account owner, tier |
| `products.csv` | Product catalogue (8 products), usage units, typical segments, products often bought together |
| `contracts.csv` | Contract headers: dates, term, auto-renew, notice period, ARR, status |
| `contract_lines.csv` | Products on each contract, annual fee and included monthly volume |
| `usage_monthly.csv` | Monthly consumption per client and product, November 2024 to October 2026 |
| `support_tickets.csv` | Support tickets with priority, category, dates and satisfaction score |
| `crm_opportunities.csv` | Renewal, upsell and cross-sell opportunities from the CRM |
| `meeting_notes/` + `meeting_notes_index.csv` | Free-text notes from account meetings (only some clients have notes) |
| `client_intel.db` | SQLite database with all of the above as tables (plus `meeting_notes` with the full text) |
| `data_dictionary.md` | Column-level definitions. Read this first. |
| `tool_catalogue.md` | Descriptions of the analyses an analyst runs today, written as tool contracts you can implement |
| `sample_requests.json` | Example requests a sales rep might send |

## Key facts

- The data was extracted on **2026-11-01**. Treat that as "today" (`as_of`). Usage is complete up to and including October 2026.
- The data came from several systems and has not been cleaned. Expect the kind of imperfections real data has.
- All money is in EUR.

## Quick start

```bash
sqlite3 client_intel.db "SELECT client_id, client_name, segment FROM clients LIMIT 5;"
```

```python
import sqlite3, pandas as pd
con = sqlite3.connect("client_intel.db")
usage = pd.read_sql("SELECT * FROM usage_monthly", con)
```

CSV and SQLite hold the same data; use whichever you prefer. Please do not edit the source files in place. If you clean data, do it in code so we can see it.

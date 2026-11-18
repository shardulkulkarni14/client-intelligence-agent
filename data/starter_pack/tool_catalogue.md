# Tool catalogue: the "things we have"

Today an analyst answers a rep's request by running roughly the analyses below. They are written as tool contracts to give you a head start. You do not need to implement all of them, and you can rename, merge, split or add tools. Implement them however you like (SQL, pandas, plain Python).

**Ground rule: every number in a briefing must come from a tool output, not from the model.** Tools should return structured results (for example JSON) that include the IDs of the rows they used, so the writer can cite them and a verifier can check them.

## Requests and triggers

A request is a client (ID or a name as the rep types it) plus a trigger, with optional free-text context from the rep. Triggers you should support:

| Trigger | The rep is asking |
|---|---|
| `renewal` | The contract is coming up for renewal. What is the position and what should I propose? |
| `meeting_prep` | I am meeting the client soon. What do I need to know? |
| `upsell` | Where can we grow this account (more volume or new products)? |
| `at_risk` | Is this account at risk, why, and what should I do? |

Different triggers need different analyses and emphasis. Deciding which ones to run is part of the task.

## Suggested tools

| Tool | Input | Returns |
|---|---|---|
| `resolve_client` | free-text name or ID | Matching `client_id`(s) with a confidence; ask or stop if ambiguous |
| `get_client_profile` | client_id | Segment, country, owner, tier, customer since |
| `get_contract_status` | client_id, as_of | Contract in force (or none), products, ARR, end date, days to end, notice deadline, auto-renew, pending contracts, ARR change at last renewal |
| `get_usage_trend` | client_id, product_id (optional), as_of | Monthly series per product, utilisation vs included volume, recent change vs the same months last year and vs the previous period, months over included volume, data gaps |
| `get_whitespace` | client_id | Products the client does not hold, how many segment peers hold them, related products to what they already hold, existing open or lost opportunities for those products |
| `get_support_summary` | client_id, as_of, window_days | Ticket counts by priority and category, open tickets, average CSAT, change vs the previous window, notable tickets |
| `get_opportunities` | client_id | Open and recently closed CRM opportunities |
| `get_meeting_notes` | client_id (optional query) | Note text with note IDs and dates |
| `check_data_quality` | client_id | Duplicates, missing months, short history, blank fields found for this client |

## Citations

Use any consistent citation style that points back to source rows or to a tool result. One simple option:

- Source rows: `[contracts:K-0002]`, `[usage:U-00422]`, `[ticket:T-0123]`, `[opp:O-0001]`, `[note:N-003]`, `[product:WIDGETS]`
- Calculated values: cite the tool call that produced them, e.g. `[calc:usage_trend#3]`, and keep the tool output (with its input row IDs) in a saved evidence file next to the briefing.

## The briefing

A useful briefing for a rep is short (about one page), leads with what matters for the trigger, and ends with concrete next steps. It typically covers some of: headline, account snapshot, contract and renewal position, usage trends, growth opportunities, support health, relationship context from notes, risks, recommended talking points and questions to ask, and a clear "data gaps and confidence" section. It should say plainly when something is unknown.

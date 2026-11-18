"""Rank every client by renewal risk and by room to grow, without a model.

The score is an ordering aid, not a probability: it says which accounts to open
first, not how likely a client is to leave. It is a plain sum of the points
below, and the weights are judgement calls, not fitted to outcomes (the data pack
holds no churn history to fit them to). Every point awarded carries the sentence
of the tool fact that earned it and that fact's citation ID, so a rank can always
be traced back to rows. The tools' own signals and thresholds are reused; no
figure is recomputed here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from client_intel.db import Dataset
from client_intel.evidence import CALC, DATA, Fact, ToolResult, fmt_eur
from client_intel.tools.claims import check_claims
from client_intel.tools.contracts import get_contract_status, get_opportunities
from client_intel.tools.quality import check_data_quality
from client_intel.tools.support import get_support_summary
from client_intel.tools.usage import get_usage_trend
from client_intel.tools.whitespace import get_whitespace

# --- renewal risk points -------------------------------------------------------
RISK_NO_CONTRACT_IN_FORCE = 40  # nothing signed covers today: the revenue is unprotected
RISK_ENDS_SOON_NO_AUTO_RENEW = 30  # it lapses within the horizon unless someone acts
RISK_RENEWAL_BELOW_VALUE = 25  # the rep's own renewal deal is already smaller than the contract
RISK_USAGE_DECLINE = 10  # per product at or beyond the usage tool's year-on-year risk threshold
RISK_USAGE_DECLINE_CAP = 20  # two falling products are a pattern; more adds little
RISK_OPEN_P1_P2 = 15  # an unresolved serious ticket during a renewal conversation
RISK_LOW_CSAT = 10  # the support tool rates the average CSAT as a risk
RISK_NOTE_DATA_CONFLICT = 10  # a note says one thing and the measured usage another
RISK_STALE_OPPORTUNITY = 10  # an open deal past its expected close date
RISK_CONTRACT_SHRANK = 10  # the current contract is smaller or shorter than the one before
RISK_TICKETS_RISING = 5  # more tickets than in the previous period; weak on its own

# --- growth points ---------------------------------------------------------------
GROWTH_OVER_INCLUDED = 15  # per product used above its included volume for a sustained period
GROWTH_OVER_INCLUDED_CAP = 30
GROWTH_USAGE_UP = 10  # per product at or beyond the usage tool's year-on-year growth threshold
GROWTH_USAGE_UP_CAP = 20
GROWTH_OPEN_EXPANSION_OPP = 15  # per open upsell or cross-sell opportunity
GROWTH_OPEN_EXPANSION_OPP_CAP = 30
GROWTH_WHITESPACE = 5  # per top white-space candidate; a hint, weaker than observed demand
GROWTH_WHITESPACE_CAP = 10

ENDS_SOON_DAYS = 90
EXPANSION_OPP_TYPES = ("upsell", "cross_sell")

PORTFOLIO_TOOLS: dict[str, Callable[[Dataset, str], ToolResult]] = {
    "data_quality": check_data_quality,
    "contract_status": get_contract_status,
    "opportunities": get_opportunities,
    "usage_trend": get_usage_trend,
    "support_summary": get_support_summary,
    "claim_check": check_claims,
    "whitespace": get_whitespace,
}


class _Score:
    """A running sum in which every point is tied to the fact that earned it."""

    def __init__(self) -> None:
        self.score = 0
        self.reasons: list[dict[str, str]] = []

    def award(self, points: int, facts: list[Fact], cap: int | None = None) -> None:
        """`points` per fact, up to `cap` in total. No fact means no points: a
        score may not rest on something the reader cannot look up."""
        awarded = 0
        for fact in facts:
            if cap is not None and awarded + points > cap:
                break
            awarded += points
            self.reasons.append({"text": fact.text, "cite": fact.id})
        self.score += awarded

    def to_dict(self) -> dict[str, Any]:
        return {"score": self.score, "reasons": self.reasons}


def _facts(result: ToolResult, topic: str, signal: str | None = None,
           kind: str | None = None) -> list[Fact]:
    return [f for f in result.facts
            if f.topic == topic
            and (signal is None or f.signal == signal)
            and (kind is None or f.kind == kind)]


def _risk(r: dict[str, ToolResult]) -> _Score:
    score = _Score()
    contract, opps, support = r["contract_status"], r["opportunities"], r["support_summary"]
    in_force = contract.data.get("in_force")
    if in_force is None:
        # The expired or pending contract the tool reports as the reason.
        why = _facts(contract, "contract", "risk") or _facts(contract, "pending_contract", "risk")
        score.award(RISK_NO_CONTRACT_IN_FORCE, why[:1])
    elif in_force["days_to_end"] <= ENDS_SOON_DAYS and in_force.get("auto_renew") != "Y":
        # The tool's first computed renewal fact is the end date and days left.
        score.award(RISK_ENDS_SOON_NO_AUTO_RENEW, _facts(contract, "renewal", kind=CALC)[:1])

    below = {f"opp:{x['opp_id']}" for x in opps.data.get("renewal_vs_contract", [])
             if x.get("pct") is not None and x["pct"] < 0}
    score.award(RISK_RENEWAL_BELOW_VALUE,
                [f for f in _facts(opps, "renewal", "risk") if below & set(f.rows)][:1])
    score.award(RISK_USAGE_DECLINE, _facts(r["usage_trend"], "usage_yoy", "risk"),
                cap=RISK_USAGE_DECLINE_CAP)
    if support.data.get("open_p1_p2_count"):
        score.award(RISK_OPEN_P1_P2, _facts(support, "open_tickets", "risk", CALC)[:1])
    # The most recent window first; either one counts once.
    low_csat = _facts(support, "csat_90d", "risk") or _facts(support, "csat_12m", "risk")
    score.award(RISK_LOW_CSAT, low_csat[:1])
    score.award(RISK_NOTE_DATA_CONFLICT, _facts(r["claim_check"], "source_conflict", "risk")[:1])
    score.award(RISK_STALE_OPPORTUNITY, _facts(opps, "stale_opportunity", "risk")[:1])
    score.award(RISK_CONTRACT_SHRANK, _facts(contract, "contract_change", "risk")[:1])
    score.award(RISK_TICKETS_RISING, _facts(support, "ticket_trend", "risk")[:1])
    return score


def _growth(r: dict[str, ToolResult]) -> _Score:
    score = _Score()
    usage, opps, space = r["usage_trend"], r["opportunities"], r["whitespace"]
    score.award(GROWTH_OVER_INCLUDED, _facts(usage, "over_included", "opportunity"),
                cap=GROWTH_OVER_INCLUDED_CAP)
    score.award(GROWTH_USAGE_UP, _facts(usage, "usage_yoy", "opportunity"),
                cap=GROWTH_USAGE_UP_CAP)
    expansion = {f"opp:{o['opp_id']}" for o in opps.data.get("open", [])
                 if o.get("opp_type") in EXPANSION_OPP_TYPES}
    score.award(GROWTH_OPEN_EXPANSION_OPP,
                [f for f in _facts(opps, "open_opportunity", kind=DATA) if f.id in expansion],
                cap=GROWTH_OPEN_EXPANSION_OPP_CAP)
    top = {f"product:{p}" for p in space.data.get("top_candidates", [])}
    score.award(GROWTH_WHITESPACE,
                [f for f in _facts(space, "whitespace", "opportunity") if f.id in top],
                cap=GROWTH_WHITESPACE_CAP)
    return score


def client_results(ds: Dataset, client_id: str) -> dict[str, ToolResult]:
    return {name: tool(ds, client_id) for name, tool in PORTFOLIO_TOOLS.items()}


def _row(ds: Dataset, client_id: str) -> dict[str, Any]:
    client = ds.clients[client_id]
    results = client_results(ds, client_id)
    # Only a contract in force gives a current value; an expired one is not shown
    # as if it still applied.
    in_force = results["contract_status"].data.get("in_force") or {}
    end = in_force.get("end_date")
    return {
        "client_id": client_id,
        "client_name": client["client_name"],
        "segment": client["segment"],
        "tier": client["tier"],
        "account_owner": client["account_owner"],
        "arr_eur": in_force.get("arr_eur"),
        "contract_id": in_force.get("contract_id"),
        "contract_end": end.isoformat() if end else None,
        "days_to_end": in_force.get("days_to_end"),
        "auto_renew": in_force.get("auto_renew"),
        "confidence": results["data_quality"].data["confidence"],
        "renewal_risk": _risk(results).to_dict(),
        "growth": _growth(results).to_dict(),
    }


def rank_portfolio(ds: Dataset) -> dict[str, Any]:
    """Every client, highest renewal risk first; ties by the nearer contract end, then ID."""
    rows = [_row(ds, client_id) for client_id in sorted(ds.clients)]
    # sorted() above fixes the ID order; the stable sort keeps it within ties.
    rows.sort(key=lambda c: (-c["renewal_risk"]["score"],
                             c["days_to_end"] if c["days_to_end"] is not None else -1))
    return {"as_of": ds.as_of.isoformat(), "clients": rows}


def _top_reason(block: dict[str, Any]) -> str:
    if not block["reasons"]:
        return "-"
    first = block["reasons"][0]
    # A pipe inside a sentence would break the table row.
    return f"{first['text'].replace('|', '/')} [{first['cite']}]"


def render_markdown(portfolio: dict[str, Any]) -> str:
    lines = [
        f"# Portfolio ranking, data as of {portfolio['as_of']}",
        "",
        "Scores are sums of fixed points per finding (see `portfolio.py`). They order "
        "the accounts; they are not probabilities.",
        "",
        "| Rank | Client | Annual value | Contract end | Risk score | Top risk reason "
        "| Growth score | Top growth reason |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for rank, c in enumerate(portfolio["clients"], start=1):
        value = fmt_eur(c["arr_eur"]) if c["arr_eur"] is not None else "none in force"
        lines.append(
            f"| {rank} | {c['client_name']} ({c['client_id']}) | {value} "
            f"| {c['contract_end'] or '-'} | {c['renewal_risk']['score']} "
            f"| {_top_reason(c['renewal_risk'])} | {c['growth']['score']} "
            f"| {_top_reason(c['growth'])} |"
        )
    return "\n".join(lines) + "\n"

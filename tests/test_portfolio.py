"""The portfolio ranking: deterministic, and every point traceable to a tool fact."""

from client_intel import portfolio
from client_intel.portfolio import client_results, rank_portfolio, render_markdown

CLIENT_KEYS = {
    "client_id", "client_name", "segment", "tier", "account_owner", "arr_eur", "contract_id",
    "contract_end", "days_to_end", "auto_renew", "confidence", "renewal_risk", "growth",
}


def test_shape_and_order(ds):
    ranking = rank_portfolio(ds)
    assert set(ranking) == {"as_of", "clients"}
    assert ranking["as_of"] == "2026-11-01"
    assert sorted(c["client_id"] for c in ranking["clients"]) == sorted(ds.clients)
    for client in ranking["clients"]:
        assert set(client) == CLIENT_KEYS
        assert client["confidence"] in ("high", "medium", "low")
        for block in (client["renewal_risk"], client["growth"]):
            assert set(block) == {"score", "reasons"}
            assert isinstance(block["score"], int)
    scores = [c["renewal_risk"]["score"] for c in ranking["clients"]]
    assert scores == sorted(scores, reverse=True)


def test_known_accounts_lead_the_renewal_risk_ranking(ds):
    ranking = rank_portfolio(ds)
    top = [c["client_id"] for c in ranking["clients"][:3]]
    assert "C001" in top and "C007" in top
    by_id = {c["client_id"]: c for c in ranking["clients"]}

    halden = by_id["C001"]
    assert (halden["arr_eur"], halden["contract_id"], halden["contract_end"]) == (
        752000.0, "K-0002", "2027-01-31")
    assert (halden["days_to_end"], halden["auto_renew"]) == (91, "Y")
    # Renewal deal below contract value, two falling products, open P1/P2, low CSAT,
    # and more tickets than in the previous period.
    assert halden["renewal_risk"]["score"] == (
        portfolio.RISK_RENEWAL_BELOW_VALUE + 2 * portfolio.RISK_USAGE_DECLINE
        + portfolio.RISK_OPEN_P1_P2 + portfolio.RISK_LOW_CSAT + portfolio.RISK_TICKETS_RISING)
    assert [r["cite"] for r in halden["renewal_risk"]["reasons"]] == [
        "calc:opportunities#1", "calc:usage_trend#3", "calc:usage_trend#10",
        "calc:support_summary#13", "calc:support_summary#10", "calc:support_summary#12"]

    varrow = by_id["C007"]
    assert (varrow["arr_eur"], varrow["contract_id"], varrow["contract_end"]) == (
        None, None, None)
    assert (varrow["days_to_end"], varrow["auto_renew"]) == (None, None)
    assert varrow["renewal_risk"]["score"] == (
        portfolio.RISK_NO_CONTRACT_IN_FORCE + portfolio.RISK_STALE_OPPORTUNITY)
    assert varrow["renewal_risk"]["reasons"][0]["cite"] == "calc:contract_status#1"
    assert "K-0011 is not in force" in varrow["renewal_risk"]["reasons"][0]["text"]


def test_every_reason_quotes_a_fact_of_that_client(ds):
    for client in rank_portfolio(ds)["clients"]:
        facts = {(f.id, f.text) for result in client_results(ds, client["client_id"]).values()
                 for f in result.facts}
        for block in (client["renewal_risk"], client["growth"]):
            assert bool(block["reasons"]) == (block["score"] > 0)
            for reason in block["reasons"]:
                assert set(reason) == {"text", "cite"}
                assert (reason["cite"], reason["text"]) in facts, (client["client_id"], reason)


def test_per_product_points_are_capped(ds):
    by_id = {c["client_id"]: c for c in rank_portfolio(ds)["clients"]}
    usage = client_results(ds, "C009")["usage_trend"]
    over = [f for f in usage.facts if f.topic == "over_included" and f.signal == "opportunity"]
    up = [f for f in usage.facts if f.topic == "usage_yoy" and f.signal == "opportunity"]
    reasons = [r["cite"] for r in by_id["C009"]["growth"]["reasons"]]
    kept_over = [f.id for f in over if f.id in reasons]
    kept_up = [f.id for f in up if f.id in reasons]
    assert len(kept_over) * portfolio.GROWTH_OVER_INCLUDED <= portfolio.GROWTH_OVER_INCLUDED_CAP
    assert len(kept_up) * portfolio.GROWTH_USAGE_UP <= portfolio.GROWTH_USAGE_UP_CAP
    assert by_id["C009"]["growth"]["score"] == 70


def test_markdown_table_has_one_row_per_client(ds):
    ranking = rank_portfolio(ds)
    lines = render_markdown(ranking).splitlines()
    rows = [line for line in lines if line.startswith("| ") and not line.startswith("| Rank")]
    assert len(rows) == len(ds.clients)
    first = ranking["clients"][0]
    assert rows[0].startswith(f"| 1 | {first['client_name']} ({first['client_id']}) |")
    assert all(row.count("|") == 9 for row in rows)

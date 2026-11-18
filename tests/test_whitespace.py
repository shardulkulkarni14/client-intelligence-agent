import re

from client_intel.db import Dataset
from client_intel.evidence import CALC, OK, PARTIAL, REPORTED
from client_intel.tools.whitespace import _held_products, _prerequisites, get_whitespace


def _candidate(result, product_id: str) -> dict:
    return next(c for c in result.data["candidates"] if c["product_id"] == product_id)


def _product_fact(result, product_id: str):
    return next(
        f for f in result.facts if f.id == f"product:{product_id}" and f.topic == "whitespace"
    )


def test_c002_holdings_and_widgets_is_top_candidate(ds: Dataset) -> None:
    result = get_whitespace(ds, "C002")
    assert result.status == OK
    assert result.data["held_products"] == ["LIVE_DATA", "STATS_ARCHIVE", "STREAM"]
    assert result.data["peer_count"] == 5
    assert result.data["candidates"][0]["product_id"] == "WIDGETS"
    assert result.data["top_candidates"] == ["WIDGETS"]

    widgets = _candidate(result, "WIDGETS")
    assert widgets["peers_holding"] == 4
    assert widgets["tickets"] == ["T-0261"]
    fact = _product_fact(result, "WIDGETS")
    assert fact.signal == "opportunity"
    assert "held by 4 of 5 segment peers (80.0%)" in fact.text
    assert "ticket:T-0261" in fact.rows
    # The ranking score is for ordering only and never appears in fact text.
    assert "score" not in fact.text.lower()
    assert "8.4" not in fact.text


def test_c002_ticket_about_unheld_product_is_quoted(ds: Dataset) -> None:
    result = get_whitespace(ds, "C002")
    ticket = next(f for f in result.facts if f.id == "ticket:T-0261")
    assert ticket.kind == REPORTED
    assert '"Do you offer embeddable live match trackers for our second-screen app?"' in (
        ticket.text
    )


def test_c002_lost_opportunity_marks_fan_insights(ds: Dataset) -> None:
    result = get_whitespace(ds, "C002")
    cand = _candidate(result, "FAN_INSIGHTS")
    assert cand["lost_opps"] == ["O-0002"]
    assert cand["signal"] == "risk"
    assert "FAN_INSIGHTS" not in result.data["top_candidates"]
    fact = _product_fact(result, "FAN_INSIGHTS")
    assert fact.signal == "risk"
    assert "pitched before and lost (O-0002)" in fact.text
    assert "opp:O-0002" in fact.rows
    lost = next(f for f in result.facts if f.id == "opp:O-0002")
    assert lost.kind == REPORTED
    assert lost.signal == "risk"
    assert '"Lost - no budget this year"' in lost.text
    assert "EUR 30,000" in lost.text


def test_c015_small_peer_group_gap_and_no_percentage(ds: Dataset) -> None:
    result = get_whitespace(ds, "C015")
    assert result.data["peer_count"] == 1
    assert [g.code for g in result.gaps] == ["small_peer_group"]
    assert not any("%" in f.text for f in result.facts)
    fact = _product_fact(result, "WIDGETS")
    assert "held by 1 of 1 segment peer (peer group too small" in fact.text
    # Lost ODDS_LIVE stays listed, marked, with the reason quoted.
    assert _candidate(result, "ODDS_LIVE")["signal"] == "risk"
    lost = next(f for f in result.facts if f.id == "opp:O-0012")
    assert '"Lost - not a sportsbook use case"' in lost.text


def test_c017_lost_stream_and_odds_live_prerequisite_blocker(ds: Dataset) -> None:
    result = get_whitespace(ds, "C017")
    assert "small_peer_group" in [g.code for g in result.gaps]
    assert result.data["top_candidates"] == []
    lost = next(f for f in result.facts if f.id == "opp:O-0014")
    assert '"Lost - rights held by league"' in lost.text
    odds_live = _candidate(result, "ODDS_LIVE")
    assert odds_live["prerequisites_missing"] == ["LIVE_DATA"]
    assert "blocker: its description says it requires Live Match Data Feed (LIVE_DATA)" in (
        _product_fact(result, "ODDS_LIVE").text
    )


def test_prerequisite_is_read_from_description_text(ds: Dataset) -> None:
    assert _prerequisites(ds, ds.products["ODDS_LIVE"]) == ["LIVE_DATA"]
    others = [p for p in ds.products if p != "ODDS_LIVE"]
    assert all(_prerequisites(ds, ds.products[p]) == [] for p in others)


def test_c012_odds_live_prerequisite_met_and_ranked_first(ds: Dataset) -> None:
    result = get_whitespace(ds, "C012")
    assert result.data["candidates"][0]["product_id"] == "ODDS_LIVE"
    fact = _product_fact(result, "ODDS_LIVE")
    assert fact.signal == "opportunity"
    assert "held by 5 of 5 segment peers (100.0%)" in fact.text
    assert "prerequisite LIVE_DATA is already held" in fact.text


def test_c007_holding_falls_back_to_expired_contract(ds: Dataset) -> None:
    held, contracts, expired = _held_products(ds, "C007")
    assert expired is True
    assert [c["contract_id"] for c in contracts] == ["K-0011"]
    assert held == {"INTEGRITY", "LIVE_DATA", "STATS_ARCHIVE"}
    result = get_whitespace(ds, "C007")
    assert result.status == PARTIAL
    gap = next(g for g in result.gaps if g.code == "holding_based_on_expired_contract")
    assert "K-0011" in gap.text and "2026-09-30" in gap.text
    assert "4 of 5 segment peers" in _product_fact(result, "FAN_INSIGHTS").text


def test_summary_counts_and_open_opportunity(ds: Dataset) -> None:
    result = get_whitespace(ds, "C008")
    summary = next(f for f in result.facts if f.topic == "whitespace_summary")
    assert summary.kind == CALC
    held = len(result.data["held_products"])
    assert summary.text.startswith(f"Client holds {held} of 8 catalogue products")
    assert _candidate(result, "WIDGETS")["open_opps"] == ["O-0006"]
    opp = next(f for f in result.facts if f.id == "opp:O-0006")
    assert "EUR 85,000" in opp.text
    assert '"Proposal sent, follow-up call booked"' in opp.text


def test_every_missing_product_has_one_fact_for_every_client(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_whitespace(ds, client_id)
        held = set(result.data["held_products"])
        listed = [c["product_id"] for c in result.data["candidates"]]
        assert sorted(listed) == sorted(set(ds.products) - held)
        if result.data["peer_count"] < 3:
            assert not any(re.search(r"\d%", f.text) for f in result.facts)


def test_unknown_client_is_explicit(ds: Dataset) -> None:
    result = get_whitespace(ds, "C999")
    assert result.status == "no_data"
    assert [g.code for g in result.gaps] == ["unknown_client"]

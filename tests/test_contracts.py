import json
from dataclasses import replace
from datetime import date

import pytest

from client_intel.db import Dataset
from client_intel.evidence import CALC, NO_DATA, OK, PARTIAL, REPORTED, ToolResult
from client_intel.tools.contracts import get_contract_status, get_opportunities


def _texts(result: ToolResult, topic: str | None = None) -> list[str]:
    return [f.text for f in result.facts if topic is None or f.topic == topic]


def _one(result: ToolResult, needle: str):
    hits = [f for f in result.facts if needle in f.text]
    assert len(hits) == 1, f"{needle!r} matched {len(hits)} facts"
    return hits[0]


# --- get_contract_status ------------------------------------------------------


def test_c001_contract_in_force(ds: Dataset) -> None:
    result = get_contract_status(ds, "C001")
    assert result.status == OK
    data = result.data
    assert data["in_force_contract_id"] == "K-0002"
    assert data["in_force"]["arr_eur"] == 752000
    assert data["in_force"]["start_date"] == date(2025, 2, 1)
    assert data["in_force"]["end_date"] == date(2027, 1, 31)
    assert data["in_force"]["term_months"] == 24
    assert data["in_force"]["auto_renew"] == "Y"
    assert data["in_force"]["days_to_end"] == 91
    assert data["in_force"]["notice_deadline"] == date(2026, 12, 2)
    assert data["in_force"]["days_to_notice_deadline"] == 31
    assert data["in_force"]["notice_deadline_passed"] is False
    assert data["held_product_ids"] == ["LIVE_DATA", "ODDS_PRE", "ODDS_LIVE", "STREAM"]
    assert data["held_products_source"] == "in_force"
    assert data["held_from_expired"] is False
    assert data["pending"] == []

    head = result.facts[0]
    assert head.id == "contracts:K-0002"
    assert head.text == (
        "Contract K-0002 is in force as of 2026-11-01: it runs 2025-02-01 to 2027-01-31 "
        "(24 months) with an annual value of EUR 752,000."
    )
    notice = _one(result, "notice deadline")
    assert notice.kind == CALC
    assert notice.rows == ["contracts:K-0002"]
    assert "2026-12-02" in notice.text and "31 days after 2026-11-01" in notice.text
    assert notice.signal == "neutral"  # 31 days away is just outside the 30-day risk window
    assert "renews automatically" in _one(result, "notice period").text
    assert "60 days" in _one(result, "notice period").text
    # Auto-renew with the deadline still ahead: nothing has rolled over, so no such fact.
    assert not any("roll over" in t for t in _texts(result))
    assert data["in_force"]["auto_renew_next_term_start"] is None
    assert _one(result, "ends on 2027-01-31").signal == "neutral"


def test_c001_lines_and_change_at_last_renewal(ds: Dataset) -> None:
    result = get_contract_status(ds, "C001")
    lines = result.data["in_force"]["lines"]
    assert [x["line_id"] for x in lines] == ["L-00005", "L-00006", "L-00007", "L-00008"]
    assert sum(x["annual_fee_eur"] for x in lines) == 752000
    live = _one(result, "(LIVE_DATA)")
    assert live.id == "contracts:K-0002"
    assert live.rows == ["contracts:K-0002", "product:LIVE_DATA"]
    assert "EUR 192,000" in live.text and "8,000" in live.text

    assert result.data["previous_contract_id"] == "K-0001"
    change = result.data["arr_change"]
    assert change["compared_to_arr_eur"] == 692000
    assert change["pct"] == pytest.approx(8.6705, abs=1e-3)
    fact = _one(result, "+8.7%")
    assert fact.kind == CALC
    assert fact.rows == ["contracts:K-0002", "contracts:K-0001"]
    assert "EUR 752,000" in fact.text and "EUR 692,000" in fact.text
    assert result.data["term_change"] is None


def test_c007_none_in_force_expired_and_pending_are_labelled(ds: Dataset) -> None:
    result = get_contract_status(ds, "C007")
    assert result.status == PARTIAL
    data = result.data
    assert data["in_force_contract_id"] is None
    assert data["in_force"] is None
    assert data["last_expired_contract_id"] == "K-0011"
    assert data["last_expired"]["arr_eur"] == 189000
    assert data["last_expired"]["days_since_end"] == 32
    assert data["pending_contract_ids"] == ["K-0045"]
    assert data["pending"][0]["arr_eur"] == 200000
    assert data["pending"][0]["signed_date"] is None
    assert data["held_product_ids"] == ["LIVE_DATA", "INTEGRITY", "STATS_ARCHIVE"]
    assert data["held_from_expired"] is True
    assert data["held_products_source"] == "last_expired"

    gap = next(g for g in result.gaps if g.code == "no_contract_in_force")
    assert gap.rows == ["contracts:K-0011", "contracts:K-0045"]
    # Nothing may read as a contract in force.
    assert not any("is in force" in t for t in _texts(result))
    for fact in result.facts:
        if "K-0045" in fact.text and "K-0011" not in fact.text:
            assert "pending" in fact.text.lower()
        if "K-0011" in fact.text and "K-0045" not in fact.text:
            assert "expired" in fact.text.lower()
    expired = _one(result, "ended 32 days before 2026-11-01")
    assert "EUR 189,000" in expired.text and "not in force" in expired.text
    assert expired.signal == "risk"
    pending = _one(result, "pending signature")
    assert pending.id == "contracts:K-0045"
    assert "not in force" in pending.text and "EUR 200,000" in pending.text

    versus = data["pending_vs_reference"]
    assert len(versus) == 1
    assert versus[0]["compared_to_contract_id"] == "K-0011"
    assert versus[0]["pct"] == pytest.approx(5.8201, abs=1e-3)
    fact = _one(result, "+5.8%")
    assert fact.rows == ["contracts:K-0045", "contracts:K-0011"]
    assert "pending (unsigned)" in fact.text and "expired" in fact.text


def test_c003_notice_deadline_passed_and_no_previous_contract(ds: Dataset) -> None:
    result = get_contract_status(ds, "C003")
    info = result.data["in_force"]
    assert result.data["in_force_contract_id"] == "K-0005"
    assert info["auto_renew"] == "N"
    assert info["notice_deadline"] == date(2026, 10, 2)
    assert info["days_to_notice_deadline"] == -30
    assert info["notice_deadline_passed"] is True
    assert info["days_to_end"] == 60
    notice = _one(result, "notice deadline")
    assert notice.signal == "risk"
    assert "was 2026-10-02" in notice.text and "passed 30 days before" in notice.text
    assert _one(result, "notice period").text == (
        "Contract K-0005 does not renew automatically and ends on its end date unless a new "
        "contract is signed; its notice period is 90 days before the end date."
    )
    assert not any("roll over" in t for t in _texts(result))
    assert info["auto_renew_next_term_start"] is None
    assert result.data["arr_change"] is None
    assert "no_previous_contract" in [g.code for g in result.gaps]


def test_c005_shortened_term_is_a_risk(ds: Dataset) -> None:
    result = get_contract_status(ds, "C005")
    assert result.data["in_force_contract_id"] == "K-0008"
    assert result.data["in_force"]["days_to_end"] == 29
    assert result.data["term_change"] == {"previous_term_months": 24, "current_term_months": 12}
    fact = _one(result, "The term changed")
    assert fact.signal == "risk"
    assert fact.rows == ["contracts:K-0007", "contracts:K-0008"]


def test_c005_auto_renew_with_passed_deadline_is_stated_not_flagged(ds: Dataset) -> None:
    # K-0008: ends 2026-11-30, 60 days notice -> deadline 2026-10-01, 31 days before the
    # extract date. Auto-renew "Y", 12-month term -> next term would start 2026-12-01.
    result = get_contract_status(ds, "C005")
    info = result.data["in_force"]
    assert info["auto_renew"] == "Y"
    assert info["notice_deadline"] == date(2026, 10, 1)
    assert info["notice_deadline_passed"] is True
    assert info["auto_renew_next_term_start"] == date(2026, 12, 1)
    rollover = _one(result, "roll over")
    assert rollover.text == (
        "The notice deadline for K-0008 passed on 2026-10-01 and the data holds no record "
        "of notice either way; with automatic renewal the contract would roll over for "
        "another 12 months from 2026-12-01 unless notice was given."
    )
    assert rollover.kind == CALC
    assert rollover.rows == ["contracts:K-0008"]
    assert (rollover.topic, rollover.signal) == ("renewal", "neutral")
    ends = _one(result, "ends on 2026-11-30")
    assert ends.text == "Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01."
    assert ends.signal == "neutral"
    passed = _one(result, "passed 31 days before")
    assert "was 2026-10-01" in passed.text
    assert passed.signal == "neutral"
    # The auto-renew position alone raises no risk; the shortened term still does.
    assert [f.text for f in result.facts if f.topic == "renewal" and f.signal == "risk"] == []


def test_only_c005_has_a_passed_deadline_on_an_auto_renew_contract(ds: Dataset) -> None:
    rolled = [
        c for c in ds.clients if any("roll over" in t for t in _texts(get_contract_status(ds, c)))
    ]
    assert rolled == ["C005"]


def test_in_force_is_the_shared_definition_for_every_client(ds: Dataset) -> None:
    for client_id in ds.clients:
        current = ds.contract_in_force(client_id)
        reported = get_contract_status(ds, client_id).data["in_force_contract_id"]
        assert reported == (current["contract_id"] if current else None)


def test_c022_notice_deadline_exactly_30_days_is_risk(ds: Dataset) -> None:
    result = get_contract_status(ds, "C022")
    assert result.data["in_force"]["notice_deadline"] == date(2026, 12, 1)
    assert result.data["in_force"]["days_to_notice_deadline"] == 30
    assert _one(result, "notice deadline").signal == "risk"


def test_c006_duplicate_contract_row_counted_once(ds: Dataset) -> None:
    result = get_contract_status(ds, "C006")
    assert result.data["in_force_contract_id"] == "K-0010"
    assert result.data["in_force"]["arr_eur"] == 176000
    assert result.data["contract_count"] == 2
    assert "multiple_contracts_in_force" not in [g.code for g in result.gaps]
    assert len(result.data["in_force"]["lines"]) == 3


def test_every_client_has_consistent_contract_output(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_contract_status(ds, client_id)
        json.dumps(result.to_dict())
        info = result.data["in_force"]
        if client_id == "C007":
            assert info is None
            continue
        assert result.status == OK
        assert sum(x["annual_fee_eur"] for x in info["lines"]) == info["arr_eur"]
        assert set(result.data["held_product_ids"]) == {x["product_id"] for x in info["lines"]}
        for fact in result.facts:
            assert fact.rows and fact.text.endswith(".")


def test_contract_status_unknown_client(ds: Dataset) -> None:
    result = get_contract_status(ds, "C999")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["no_contracts"]
    assert result.data["held_product_ids"] == []


# --- get_opportunities --------------------------------------------------------


def test_o0001_renewal_is_a_downsell(ds: Dataset) -> None:
    result = get_opportunities(ds, "C001")
    assert result.status == OK
    assert [o["opp_id"] for o in result.data["open"]] == ["O-0001"]
    assert result.data["closed"] == []
    entry = result.data["renewal_vs_contract"][0]
    assert entry["amount_eur"] == 541500
    assert entry["arr_eur"] == 752000
    assert entry["contract_id"] == "K-0002"
    assert entry["contract_in_force"] is True
    assert entry["pct"] == pytest.approx(-27.992, abs=1e-3)
    fact = _one(result, "-28.0%")
    assert fact.kind == CALC
    assert fact.signal == "risk"
    assert fact.rows == ["opp:O-0001", "contracts:K-0002"]
    assert "EUR 541,500" in fact.text and "EUR 752,000" in fact.text

    row = result.facts[0]
    assert row.id == "opp:O-0001"
    assert row.text == (
        "Opportunity O-0001 is an open renewal opportunity at stage Negotiation, with an "
        "amount of EUR 541,500, created 2026-09-15 and expected close date 2027-01-15."
    )
    quote = result.facts[1]
    assert quote.kind == REPORTED
    assert quote.id == "opp:O-0001"
    assert '"Client asked for pricing on reduced in-play scope"' in quote.text
    assert result.data["no_renewal_opportunity"] is False
    assert result.data["stale_opp_ids"] == []


def test_c007_stale_renewal_compared_with_expired_contract(ds: Dataset) -> None:
    result = get_opportunities(ds, "C007")
    assert result.data["stale_opp_ids"] == ["O-0005"]
    stale = _one(result, "is stale")
    assert stale.signal == "risk"
    assert "2026-09-30" in stale.text and "32 days before 2026-11-01" in stale.text
    entry = result.data["renewal_vs_contract"][0]
    assert entry["contract_id"] == "K-0011"
    assert entry["contract_in_force"] is False
    versus = _one(result, "+5.8%")
    assert "expired contract (none is in force) K-0011" in versus.text
    # No contract in force, so the "ending soon without a renewal" check does not apply.
    assert result.data["no_renewal_opportunity"] is False


def test_only_o0005_is_stale_across_all_clients(ds: Dataset) -> None:
    stale = [i for c in ds.clients for i in get_opportunities(ds, c).data["stale_opp_ids"]]
    assert stale == ["O-0005"]


def test_c009_won_upsell_not_reflected_in_contract(ds: Dataset) -> None:
    result = get_opportunities(ds, "C009")
    assert [o["opp_id"] for o in result.data["open"]] == ["O-0007"]
    assert [o["opp_id"] for o in result.data["closed"]] == ["O-0008"]
    assert result.data["open_product_ids"] == ["STREAM"]
    assert result.data["won_not_contracted"] == [
        {
            "opp_id": "O-0008",
            "product_id": "LIVE_DATA",
            "amount_eur": 40000,
            "latest_contract_id": "K-0015",
        }
    ]
    gap = next(g for g in result.gaps if g.code == "won_not_contracted")
    assert gap.rows == ["opp:O-0008", "contracts:K-0015"]
    assert "EUR 40,000" in gap.text and "2025-10-01" in gap.text and "2024-11-30" in gap.text
    assert _one(result, "is Closed Won, but").topic == "source_conflict"


def test_won_not_contracted_only_for_c009_and_c013(ds: Dataset) -> None:
    flagged = {
        c: [w["opp_id"] for w in get_opportunities(ds, c).data["won_not_contracted"]]
        for c in ds.clients
    }
    assert {c: ids for c, ids in flagged.items() if ids} == {"C009": ["O-0008"], "C013": ["O-0011"]}
    # O-0004 (C004, new business) was followed by contract K-0006 and is not flagged.
    assert flagged["C004"] == []


def test_lost_products_keep_their_reason(ds: Dataset) -> None:
    result = get_opportunities(ds, "C017")
    assert result.data["lost_product_ids"] == ["STREAM"]
    assert result.data["lost_products"] == [
        {"product_id": "STREAM", "opp_id": "O-0014", "reason": "Lost - rights held by league"}
    ]
    assert result.data["open_product_ids"] == []
    assert "closed cross-sell opportunity for Live Streaming (STREAM) with stage Closed Lost" in (
        result.facts[0].text
    )


def test_no_renewal_opportunity_within_180_days(ds: Dataset) -> None:
    flagged = sorted(
        c for c in ds.clients if get_opportunities(ds, c).data["no_renewal_opportunity"]
    )
    assert flagged == ["C005", "C006", "C013", "C016", "C020", "C022"]
    # C013's contract ends exactly 180 days out and is included.
    result = get_opportunities(ds, "C013")
    gap = next(g for g in result.gaps if g.code == "no_renewal_opportunity")
    assert gap.rows == ["contracts:K-0023"]
    assert "180 days after 2026-11-01" in gap.text


def test_client_without_opportunities(ds: Dataset) -> None:
    result = get_opportunities(ds, "C014")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["no_opportunities"]
    assert result.data["open"] == [] and result.data["closed"] == []
    assert result.data["lost_product_ids"] == [] and result.data["open_product_ids"] == []


def test_c005_no_opportunities_but_renewal_gap_still_raised(ds: Dataset) -> None:
    result = get_opportunities(ds, "C005")
    assert result.status == NO_DATA
    assert sorted(g.code for g in result.gaps) == ["no_opportunities", "no_renewal_opportunity"]
    fact = _one(result, "no renewal opportunity")
    assert fact.text == (
        "Contract K-0008 ends on 2026-11-30, 29 days after 2026-11-01, and no renewal "
        "opportunity is recorded; the contract auto-renews."
    )
    assert fact.signal == "neutral"
    gap = next(g for g in result.gaps if g.code == "no_renewal_opportunity")
    assert gap.text == fact.text


def test_no_renewal_opportunity_is_a_risk_only_without_auto_renew(ds: Dataset) -> None:
    # Every client flagged on the real data auto-renews, so none of them is a risk.
    for client_id in ["C005", "C006", "C013", "C016", "C020", "C022"]:
        fact = _one(get_opportunities(ds, client_id), "no renewal opportunity")
        assert fact.text.endswith("the contract auto-renews.")
        assert fact.signal == "neutral"
    # C003's K-0005 (auto_renew "N", ends 2026-12-31) has renewal opportunity O-0003 in
    # the pack. Without it the contract ends with nothing lined up.
    assert "O-0003" in [o["opp_id"] for o in get_opportunities(ds, "C003").data["open"]]
    assert get_opportunities(ds, "C003").data["no_renewal_opportunity"] is False
    bare = replace(ds, opportunities=[o for o in ds.opportunities if o["client_id"] != "C003"])
    fact = _one(get_opportunities(bare, "C003"), "no renewal opportunity")
    assert fact.text == (
        "Contract K-0005 ends on 2026-12-31, 60 days after 2026-11-01, and no renewal "
        "opportunity is recorded; the contract does not auto-renew and ends unless a new "
        "one is signed."
    )
    assert fact.signal == "risk"


def test_every_opportunity_appears_once_and_serialises(ds: Dataset) -> None:
    seen: list[str] = []
    for client_id in ds.clients:
        result = get_opportunities(ds, client_id)
        json.dumps(result.to_dict())
        seen += [o["opp_id"] for o in result.data["open"] + result.data["closed"]]
    assert sorted(seen) == [f"O-{n:04d}" for n in range(1, 20)]


def test_notice_period_is_stated_for_contracts_that_are_not_in_force(ds):
    # C007 has no contract in force; both of its contracts carry 90 days of notice,
    # and a briefing must not say that no notice period is on record.
    from client_intel.tools.contracts import get_contract_status

    texts = " ".join(f.text for f in get_contract_status(ds, "C007").facts)
    assert "Its notice period was 90 days before the end date." in texts
    assert "Its drafted notice period is 90 days before the end date." in texts

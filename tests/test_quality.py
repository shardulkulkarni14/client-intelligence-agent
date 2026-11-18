"""check_data_quality against the known problems in the starter pack."""

from client_intel.db import Dataset
from client_intel.evidence import OK, PARTIAL
from client_intel.tools.quality import check_data_quality, rate_confidence


def _codes(ds: Dataset, client_id: str) -> list[str]:
    return check_data_quality(ds, client_id).data["codes"]


def test_c006_duplicates_reported_once_each(ds: Dataset) -> None:
    result = check_data_quality(ds, "C006")
    by_code = {g.code: g for g in result.gaps}
    # K-0010 appears twice in contracts; U-00422 / U-01991 are one 2026-08 record.
    assert by_code["duplicate_row"].rows == ["contracts:K-0010"]
    assert by_code["duplicate_natural_key"].rows == ["usage:U-00422", "usage:U-01991"]
    assert [g.code for g in result.gaps].count("duplicate_natural_key") == 1
    assert result.data["confidence"] == "medium"
    assert result.status == PARTIAL


def test_c010_duplicate_ticket(ds: Dataset) -> None:
    result = check_data_quality(ds, "C010")
    assert [(g.code, g.rows) for g in result.gaps] == [("duplicate_row", ["ticket:T-0281"])]
    assert result.data["confidence"] == "medium"


def test_c005_missing_march_per_product(ds: Dataset) -> None:
    result = check_data_quality(ds, "C005")
    missing = [g for g in result.gaps if g.code == "missing_month"]
    assert len(missing) == 4
    assert all("2026-03" in g.text and "unknown, not zero" in g.text for g in missing)
    assert result.data["codes"] == ["missing_month", "no_opportunities"]
    assert result.data["confidence"] == "medium"


def test_c004_short_history_and_no_context(ds: Dataset) -> None:
    result = check_data_quality(ds, "C004")
    assert result.data["codes"] == ["short_history", "no_support_tickets", "no_meeting_notes"]
    assert result.data["confidence"] == "low"
    short = next(g for g in result.gaps if g.code == "short_history")
    assert "only 2 months" in short.text
    assert short.rows == ["usage:U-00265", "usage:U-00266"]


def test_c007_no_contract_in_force_and_blank_included(ds: Dataset) -> None:
    result = check_data_quality(ds, "C007")
    assert result.data["codes"] == ["blank_included_units", "no_contract_in_force"]
    assert result.data["confidence"] == "low"
    blank_rows = sorted(r for g in result.gaps if g.code == "blank_included_units" for r in g.rows)
    assert blank_rows == ["usage:U-00500", "usage:U-00501", "usage:U-00502"]
    contract = next(g for g in result.gaps if g.code == "no_contract_in_force")
    assert sorted(contract.rows) == ["contracts:K-0011", "contracts:K-0045"]
    assert "K-0045 (pending_signature)" in contract.text
    # The severe reason is listed first.
    assert result.data["reasons"][0] == contract.text


def test_clean_client_is_high(ds: Dataset) -> None:
    result = check_data_quality(ds, "C002")
    assert result.status == OK
    assert result.gaps == []
    assert result.data == {"confidence": "high", "reasons": [], "codes": []}
    assert len(result.facts) == 1
    assert result.facts[0].topic == "confidence"
    assert result.facts[0].text.startswith("Data confidence for C002 is high")


def test_one_missing_context_source_stays_high_two_is_medium(ds: Dataset) -> None:
    # C013 has tickets and an opportunity but no notes; C012 has neither notes nor opps.
    assert _codes(ds, "C013") == ["no_meeting_notes"]
    assert check_data_quality(ds, "C013").data["confidence"] == "high"
    assert _codes(ds, "C012") == ["no_meeting_notes", "no_opportunities"]
    assert check_data_quality(ds, "C012").data["confidence"] == "medium"


def test_no_product_coverage_mismatch_in_the_pack(ds: Dataset) -> None:
    for client_id in ds.clients:
        codes = _codes(ds, client_id)
        assert "usage_without_contract_line" not in codes
        assert "contract_product_without_usage" not in codes


def test_confidence_rule() -> None:
    assert rate_confidence([]) == "high"
    assert rate_confidence(["no_meeting_notes"]) == "high"
    assert rate_confidence(["no_meeting_notes", "no_support_tickets"]) == "medium"
    assert rate_confidence(["duplicate_row"]) == "medium"
    assert rate_confidence(["duplicate_row", "short_history"]) == "low"
    assert rate_confidence(["conflicting_natural_key"]) == "low"


def test_unknown_client(ds: Dataset) -> None:
    result = check_data_quality(ds, "C999")
    assert result.data["codes"] == ["unknown_client"]
    assert result.data["confidence"] == "low"

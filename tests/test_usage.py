"""get_usage_trend against real rows in the starter pack. Expected values were computed
by hand from the usage_monthly rows quoted in the comments."""

import pytest

from client_intel.db import Dataset
from client_intel.evidence import CALC, NO_DATA, OK, PARTIAL
from client_intel.tools.usage import (
    get_usage_trend,
    last_complete_month,
    month_label,
    shift_month,
)


def _product(ds: Dataset, client_id: str, product_id: str) -> dict:
    return get_usage_trend(ds, client_id).data["products"][product_id]


def _fact(ds: Dataset, client_id: str, product_id: str, topic: str):
    facts = [
        f
        for f in get_usage_trend(ds, client_id).facts
        if f.topic == topic and f.text.startswith(product_id)
    ]
    assert len(facts) == 1, f"expected one {topic} fact for {product_id}, got {len(facts)}"
    return facts[0]


def test_month_helpers(ds: Dataset) -> None:
    assert last_complete_month(ds.as_of) == "2026-10"
    assert shift_month("2026-01", -3) == "2025-10"
    assert shift_month("2025-12", 1) == "2026-01"
    assert month_label(["2026-08", "2026-09", "2026-10"]) == "Aug-Oct 2026"
    assert month_label(["2025-12", "2026-01"]) == "Dec 2025-Jan 2026"
    assert month_label(["2026-08", "2026-10"]) == "Aug 2026, Oct 2026"


def test_year_on_year_hand_computed_c002_stream(ds: Dataset) -> None:
    # Aug-Oct 2026: 940 + 1102 + 1064 = 3106. Aug-Oct 2025: 780 + 819 + 882 = 2481.
    # (3106 - 2481) / 2481 = 25.19%.
    p = _product(ds, "C002", "STREAM")
    assert p["recent_total"] == 3106
    assert p["year_ago_total"] == 2481
    assert p["yoy_pct"] == pytest.approx(25.191, abs=0.001)
    fact = _fact(ds, "C002", "STREAM", "usage_yoy")
    assert fact.text == (
        "STREAM (Live Streaming): 3,106 streamed hours in Aug-Oct 2026 versus 2,481 in "
        "Aug-Oct 2025, a change of +25.2% year on year."
    )
    assert fact.kind == CALC
    assert fact.id.startswith("calc:usage_trend#")
    assert fact.signal == "opportunity"
    assert sorted(fact.rows) == [
        "usage:U-00126",
        "usage:U-00129",
        "usage:U-00132",
        "usage:U-00162",
        "usage:U-00165",
        "usage:U-00168",
    ]


def test_prior_period_is_labelled_not_seasonally_adjusted(ds: Dataset) -> None:
    # May-Jul 2026: 895 + 751 + 769 = 2415. (3106 - 2415) / 2415 = 28.61%.
    p = _product(ds, "C002", "STREAM")
    assert p["prior_total"] == 2415
    fact = _fact(ds, "C002", "STREAM", "usage_prior_period")
    assert "+28.6%" in fact.text
    assert "not seasonally adjusted" in fact.text


def test_over_included_count_is_numeric_not_text(ds: Dataset) -> None:
    # C002 STREAM, included 780, Nov 2025-Oct 2026:
    # 911 885 925 957 946 967 895 751 769 940 1102 1064 -> 10 months above 780.
    # A text comparison gets 8, because '1102' < '780' and '1064' < '780' as strings.
    p = _product(ds, "C002", "STREAM")
    assert p["months_over_included"] == 10
    assert p["months_over_compared"] == 12
    assert "2026-09" in p["months_over_list"] and "2026-10" in p["months_over_list"]
    as_text = sum(
        1
        for row in p["series"][-12:]
        if str(int(row["units_used"])) > str(int(row["included_units"]))
    )
    assert as_text == 8
    fact = _fact(ds, "C002", "STREAM", "over_included")
    assert "10 of the last 12 months" in fact.text
    assert fact.signal == "opportunity"
    assert len(fact.rows) == 12


def test_utilisation_and_indicative_overage_c002_stream(ds: Dataset) -> None:
    # Latest: 1064 / 780 = 136.4%. Last three months: 3106 / 2340 = 132.7%.
    # Overage: 160 + 322 + 284 = 766 hours; 766 * EUR 55 (L-00013 on K-0004) = 42,130.
    p = _product(ds, "C002", "STREAM")
    assert p["latest"]["utilisation_pct"] == pytest.approx(136.410, abs=0.001)
    assert p["utilisation_recent_pct"] == pytest.approx(132.735, abs=0.001)
    assert p["overage_units_recent"] == 766
    assert p["overage_rate_eur_per_unit"] == 55.0
    assert p["overage_eur_indicative"] == 42130
    assert "a utilisation of 136.4%" in _fact(ds, "C002", "STREAM", "usage_latest").text
    assert "132.7%" in _fact(ds, "C002", "STREAM", "utilisation").text
    overage = _fact(ds, "C002", "STREAM", "overage")
    assert "766 streamed hours" in overage.text
    assert "indicative EUR 42,130" in overage.text
    assert "contract_lines:L-00013" in overage.rows
    assert "contracts:K-0004" in overage.rows


def test_c006_duplicate_august_counted_once(ds: Dataset) -> None:
    # U-00422 and U-01991 are the same 2026-08 record (2176). Counted once:
    # 2176 + 2728 + 2563 = 7467 (8,364 a year earlier -> -10.7%), not 9643.
    p = _product(ds, "C006", "LIVE_DATA")
    august = [row for row in p["series"] if row["month"] == "2026-08"]
    assert len(august) == 1
    assert august[0]["usage_id"] == "U-00422"
    assert p["history_months"] == 24
    assert p["recent_total"] == 7467
    assert p["year_ago_total"] == 8364
    fact = _fact(ds, "C006", "LIVE_DATA", "usage_yoy")
    assert "7,467 API calls (thousands)" in fact.text
    assert "-10.7%" in fact.text
    assert fact.signal == "neutral"
    assert "usage:U-00422" in fact.rows
    assert "usage:U-01991" not in fact.rows


def test_c005_missing_march_is_a_gap_not_zero(ds: Dataset) -> None:
    result = get_usage_trend(ds, "C005")
    assert result.status == PARTIAL
    products = result.data["products"]
    assert sorted(products) == ["LIVE_DATA", "STATS_ARCHIVE", "STREAM", "WIDGETS"]
    for p in products.values():
        assert p["missing_months"] == ["2026-03"]
        assert p["history_months"] == 23
        assert all(row["month"] != "2026-03" for row in p["series"])
        assert "missing_month" in p["flags"]
    gaps = [g for g in result.gaps if g.code == "missing_month"]
    assert len(gaps) == 4
    assert all("2026-03" in g.text and "unknown, not zero" in g.text for g in gaps)
    # March is outside both comparison windows, so year on year is still computed:
    # STREAM 459 + 587 + 524 = 1570 versus 485 + 498 + 528 = 1511 -> +3.9%.
    stream = products["STREAM"]
    assert stream["recent_total"] == 1570
    assert stream["year_ago_total"] == 1511
    assert "+3.9%" in _fact(ds, "C005", "STREAM", "usage_yoy").text


def test_c004_short_history_gives_no_year_on_year(ds: Dataset) -> None:
    result = get_usage_trend(ds, "C004")
    assert result.status == PARTIAL
    p = result.data["products"]["LIVE_DATA"]
    assert p["history_months"] == 2
    assert p["yoy_pct"] is None
    assert p["prior_period_pct"] is None
    assert p["missing_months"] == []
    assert [g.code for g in result.gaps] == ["short_history"]
    topics = {f.topic for f in result.facts}
    assert "usage_yoy" not in topics
    assert "usage_prior_period" not in topics
    # 800 / 2000 = 40.0% in October; (523 + 800) / 4000 = 33.1% over the two months held.
    assert "a utilisation of 40.0%" in _fact(ds, "C004", "LIVE_DATA", "usage_latest").text
    util = _fact(ds, "C004", "LIVE_DATA", "utilisation")
    assert "33.1%" in util.text
    assert util.signal == "risk"
    assert "low_utilisation_risk" in p["signals"]


def test_c007_blank_included_units_is_a_gap(ds: Dataset) -> None:
    result = get_usage_trend(ds, "C007")
    gaps = [g for g in result.gaps if g.code == "blank_included_units"]
    assert sorted(row for g in gaps for row in g.rows) == [
        "usage:U-00500",
        "usage:U-00501",
        "usage:U-00502",
    ]
    p = result.data["products"]["LIVE_DATA"]
    assert p["latest"]["units_used"] == 2966
    assert p["latest"]["included_units"] is None
    assert p["latest"]["utilisation_pct"] is None
    latest = _fact(ds, "C007", "LIVE_DATA", "usage_latest")
    assert latest.text == (
        "LIVE_DATA (Live Match Data Feed): 2,966 API calls (thousands) used in Oct 2026."
    )
    # Utilisation only over the two months with a known included volume:
    # (3038 + 3500) / (4500 + 4500) = 72.6%.
    assert p["utilisation_recent_months"] == ["2026-08", "2026-09"]
    assert p["utilisation_recent_pct"] == pytest.approx(72.644, abs=0.001)
    assert p["months_over_compared"] == 11


def test_decimal_units_keep_one_decimal(ds: Dataset) -> None:
    # WIDGETS is reported with one decimal in the source; the text must not round it away.
    fact = _fact(ds, "C009", "WIDGETS", "usage_latest")
    assert "53.2 widget impressions (millions)" in fact.text
    assert "48.0 included" in fact.text


def test_clean_client_is_ok_and_products_are_separate(ds: Dataset) -> None:
    result = get_usage_trend(ds, "C002")
    assert result.status == OK
    assert result.gaps == []
    assert sorted(result.data["products"]) == ["LIVE_DATA", "STATS_ARCHIVE", "STREAM"]
    assert result.data["last_complete_month"] == "2026-10"
    # Every fact is about exactly one product and cites usage rows.
    for fact in result.facts:
        assert fact.kind == CALC
        assert any(row.startswith("usage:U-") for row in fact.rows)


def test_unknown_client_returns_no_data(ds: Dataset) -> None:
    result = get_usage_trend(ds, "C999")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["no_usage_data"]


def test_result_is_json_serialisable(ds: Dataset) -> None:
    import json

    json.dumps(get_usage_trend(ds, "C007").to_dict())

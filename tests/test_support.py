from client_intel.db import Dataset
from client_intel.evidence import NO_DATA, OK, REPORTED
from client_intel.tools.support import MAX_ROWS, get_support_summary


def _fact(result, topic: str, contains: str = ""):
    return next(f for f in result.facts if f.topic == topic and contains in f.text)


def test_c004_has_no_tickets_and_says_so(ds: Dataset) -> None:
    result = get_support_summary(ds, "C004")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["no_support_tickets"]
    assert "not that the client has no problems" in result.gaps[0].text


def test_c010_duplicate_ticket_counted_once(ds: Dataset) -> None:
    result = get_support_summary(ds, "C010")
    assert result.data["total_tickets"] == 16
    assert result.data["all_ticket_ids"].count("T-0281") == 1
    assert result.data["windows"]["90d"]["ticket_ids"].count("T-0281") == 1
    assert result.data["windows"]["90d"]["count"] == 4
    assert result.facts[0].text.startswith("16 tickets on record in total")


def test_c001_open_tickets_exact(ds: Dataset) -> None:
    result = get_support_summary(ds, "C001")
    assert result.status == OK
    assert result.data["open_count"] == 2
    assert [t["ticket_id"] for t in result.data["open_tickets"]] == ["T-0279", "T-0284"]
    assert [t["age_days"] for t in result.data["open_tickets"]] == [20, 11]
    summary = _fact(result, "open_tickets", "open tickets at")
    assert summary.text == "2 open tickets at 2026-11-01, of which 2 are P1/P2."
    assert summary.signal == "risk"
    p1 = next(f for f in result.facts if f.id == "ticket:T-0284")
    assert p1.kind == REPORTED
    assert p1.signal == "risk"
    assert "priority P1" in p1.text
    assert "open for 11 days" in p1.text
    assert '"In-play latency spike during evening fixtures"' in p1.text


def test_c001_csat_and_window_counts_exact(ds: Dataset) -> None:
    result = get_support_summary(ds, "C001")
    year = result.data["windows"]["12m"]
    assert year["count"] == 12
    assert year["by_priority"] == {"P1": 5, "P2": 6, "P3": 1}
    assert year["p1_p2_count"] == 11
    assert year["csat_rated"] == 9
    assert round(year["csat_avg"], 4) == round(20 / 9, 4)
    csat_year = _fact(result, "csat_12m")
    assert csat_year.text == (
        "Average CSAT in the last 12 months is 2.2 out of 5, from 9 rated tickets."
    )
    assert csat_year.signal == "risk"
    csat_90 = _fact(result, "csat_90d")
    assert csat_90.text == "Average CSAT in the last 90 days is 1.2 out of 5, from 4 rated tickets."
    assert sorted(csat_90.rows) == [
        "ticket:T-0249",
        "ticket:T-0255",
        "ticket:T-0259",
        "ticket:T-0269",
    ]
    assert "Latency (5), Data accuracy (2), Access (1)" in _fact(result, "support_12m", "Top").text


def test_c001_rising_volume_counts_only(ds: Dataset) -> None:
    result = get_support_summary(ds, "C001")
    trend = _fact(result, "ticket_trend")
    assert trend.text == (
        "Ticket volume is up: 7 opened in the last 90 days versus 2 in the previous 90 days."
    )
    assert "%" not in trend.text
    assert trend.signal == "risk"
    assert result.data["trend"]["previous_ids"] == ["T-0237", "T-0242"]


def test_c024_open_p4_is_not_a_risk_and_csat_is_na(ds: Dataset) -> None:
    result = get_support_summary(ds, "C024")
    assert result.data["open_count"] == 1
    assert result.data["open_p1_p2_count"] == 0
    assert _fact(result, "open_tickets", "open ticket at").signal == "neutral"
    assert next(f for f in result.facts if f.id == "ticket:T-0286").signal == "neutral"
    assert _fact(result, "csat_12m").text == (
        "Average CSAT in the last 12 months: n/a, no rated tickets."
    )
    assert result.data["windows"]["12m"]["csat_avg"] is None
    # One ticket against none is not a rising count.
    assert _fact(result, "ticket_trend").signal == "neutral"


def test_c015_quiet_windows_are_stated_not_skipped(ds: Dataset) -> None:
    result = get_support_summary(ds, "C015")
    assert result.status == OK
    assert result.data["total_tickets"] == 7
    assert result.data["windows"]["90d"]["count"] == 0
    assert _fact(result, "support_90d").text == (
        "No tickets were opened in the last 90 days (after 2026-08-03)."
    )
    assert _fact(result, "open_tickets").text == "No open tickets at 2026-11-01."
    # Two ratings are too few to call a CSAT risk either way.
    assert result.data["windows"]["12m"]["csat_rated"] == 2


def test_calc_rows_are_capped_and_ticket_cited(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_support_summary(ds, client_id)
        for fact in result.facts:
            assert len(fact.rows) <= MAX_ROWS
            assert all(r.startswith("ticket:T-") for r in fact.rows)
        if result.status == OK:
            assert len(result.data["all_ticket_ids"]) == result.data["total_tickets"]

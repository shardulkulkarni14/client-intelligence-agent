import pytest

from client_intel.db import Dataset
from client_intel.evidence import CALC, DATA, NO_DATA, OK
from client_intel.tools import support
from client_intel.tools.support import MAX_NOTABLE_TICKETS, MAX_ROWS, get_support_summary


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
    assert p1.kind == DATA  # recorded fields; only the subject is quoted wording
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
    # Scores 1, 1, 2, 1 average 1.25, which rounds half up to 1.3.
    assert result.data["windows"]["90d"]["csat_avg"] == 1.25
    assert csat_90.text == "Average CSAT in the last 90 days is 1.3 out of 5, from 4 rated tickets."
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


def _notable(result) -> list:
    return [f for f in result.facts if f.topic == "notable_tickets"]


def test_c003_closed_ticket_that_explains_usage_reaches_the_writer(ds: Dataset) -> None:
    result = get_support_summary(ds, "C003")
    facts = _notable(result)
    # T-0258 is the only ticket of the last 90 days; the other three are P1/P2 within 12 months.
    assert [f.id for f in facts] == [
        "ticket:T-0258",
        "ticket:T-0243",
        "ticket:T-0222",
        "ticket:T-0146",
    ]
    assert all(f.kind == DATA and f.rows == [f.id] for f in facts)
    assert facts[0].text == (
        "Ticket T-0258: closed, priority P3, category Integration, product STREAM, opened "
        "2026-08-28, closed 2026-09-02 after 5 days, CSAT 4 out of 5; subject as written by "
        'the client: "Request to pause streams for cup matches moved to free-to-air partner".'
    )
    # Unrated ticket: no CSAT part. One day is singular.
    assert facts[1].text == (
        "Ticket T-0243: closed, priority P2, category Outage, product STATS_ARCHIVE, opened "
        "2026-07-19, closed 2026-07-20 after 1 day; subject as written by the client: "
        '"Feed unavailable for 20 minutes".'
    )
    assert [t["ticket_id"] for t in result.data["notable_tickets"]] == [
        "T-0258",
        "T-0243",
        "T-0222",
        "T-0146",
    ]
    assert result.data["notable_tickets"][0]["days_to_close"] == 5
    assert result.data["notable_left_out_count"] == 0


def test_c001_notable_tickets_newest_first_without_the_open_ones(ds: Dataset) -> None:
    result = get_support_summary(ds, "C001")
    facts = _notable(result)
    # 12 tickets qualify (7 in the last 90 days, 11 P1/P2 in 12 months); 2 of them are open.
    assert [f.id for f in facts] == [
        "ticket:T-0273",
        "ticket:T-0269",
        "ticket:T-0259",
        "ticket:T-0255",
        "ticket:T-0249",
        "ticket:T-0242",
        "ticket:T-0237",
        "ticket:T-0203",
        "ticket:T-0169",
        "ticket:T-0151",
    ]
    assert len(facts) == MAX_NOTABLE_TICKETS
    assert all(f.kind == DATA for f in facts)
    assert result.data["notable_left_out_count"] == 0
    # The P3 ticket is listed because it is recent; older P3 tickets are not.
    assert "priority P3" in facts[2].text
    assert "T-0083" not in [t["ticket_id"] for t in result.data["notable_tickets"]]
    same_day = next(f for f in facts if f.id == "ticket:T-0255")
    assert "opened 2026-08-23, closed 2026-08-23 after 0 days, CSAT 1 out of 5" in same_day.text
    # Open tickets keep their own fact and are not repeated.
    for open_id in ("ticket:T-0279", "ticket:T-0284"):
        assert [f.topic for f in result.facts if f.id == open_id] == ["open_tickets"]


def test_no_ticket_is_emitted_twice_for_any_client(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_support_summary(ds, client_id)
        ids = [f.id for f in result.facts if f.id.startswith("ticket:")]
        assert len(ids) == len(set(ids))
        assert len(_notable(result)) <= MAX_NOTABLE_TICKETS


def test_c015_has_no_notable_tickets(ds: Dataset) -> None:
    result = get_support_summary(ds, "C015")
    assert _notable(result) == []
    assert result.data["notable_tickets"] == []


def test_notable_cap_says_how_many_were_left_out(
    ds: Dataset, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(support, "MAX_NOTABLE_TICKETS", 3)
    result = get_support_summary(ds, "C001")
    facts = _notable(result)
    assert [f.id for f in facts[:3]] == ["ticket:T-0273", "ticket:T-0269", "ticket:T-0259"]
    assert len(facts) == 4
    left_out = facts[3]
    assert left_out.kind == CALC
    assert left_out.text == (
        "7 further tickets that are no longer open, opened in the last 90 days or P1/P2 in "
        "the last 365 days, are not listed one by one; only the 3 most recent are."
    )
    assert left_out.rows == [
        "ticket:T-0255",
        "ticket:T-0249",
        "ticket:T-0242",
        "ticket:T-0237",
        "ticket:T-0203",
        "ticket:T-0169",
        "ticket:T-0151",
    ]
    # The full list stays in data, with a flag for what was listed.
    assert len(result.data["notable_tickets"]) == 10
    assert [t["listed"] for t in result.data["notable_tickets"]] == [True] * 3 + [False] * 7
    assert result.data["notable_left_out_count"] == 7

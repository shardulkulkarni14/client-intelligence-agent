from datetime import date

from client_intel import db


def test_types_are_cast_and_blanks_are_none(ds):
    contract = next(c for c in ds.contracts if c["contract_id"] == "K-0001")
    assert contract["arr_eur"] == 692000.0
    assert contract["end_date"] == date(2025, 1, 31)
    pending = next(c for c in ds.contracts if c["status"] == "pending_signature")
    assert pending["signed_date"] is None


def test_exact_duplicate_rows_are_counted_once_and_reported(ds):
    assert sum(1 for c in ds.contracts if c["contract_id"] == "K-0010") == 1
    assert sum(1 for t in ds.tickets if t["ticket_id"] == "T-0281") == 1
    codes = {(i.table, i.code) for i in ds.issues}
    assert ("contracts", "duplicate_row") in codes
    assert ("support_tickets", "duplicate_row") in codes


def test_same_usage_month_under_two_ids_is_counted_once(ds):
    rows = [
        u
        for u in ds.usage
        if (u["client_id"], u["product_id"], u["month"]) == ("C006", "LIVE_DATA", "2026-08")
    ]
    assert len(rows) == 1
    issue = next(i for i in ds.issues if i.code == "duplicate_natural_key")
    assert set(issue.rows) == {"U-00422", "U-01991"}


def test_row_counts_after_cleaning(ds):
    assert len(ds.clients) == 25
    assert len(ds.contracts) == 45
    assert len(ds.tickets) == 288
    assert len(ds.usage) == 1990


def test_blank_included_units_stay_unknown(ds):
    blanks = [u for u in ds.usage if u["included_units"] is None]
    assert {u["usage_id"] for u in blanks} == {"U-00500", "U-00501", "U-00502"}
    assert db.AS_OF == date(2026, 11, 1)

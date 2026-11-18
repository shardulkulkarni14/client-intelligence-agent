from client_intel.tools.claims import check_claims, product_keywords


def test_keywords_identify_one_product_each(ds):
    keywords = product_keywords(ds)
    assert keywords["stream"] == "STREAM"
    assert keywords["integr"] == "INTEGRITY"
    assert "live" not in keywords and "match" not in keywords


def test_note_claiming_growth_conflicts_with_measured_decline(ds):
    result = check_claims(ds, "C003")
    conflict = next(f for f in result.facts if f.topic == "source_conflict")
    assert "N-006" in conflict.text and "-22.6%" in conflict.text
    assert "note:N-006" in conflict.rows
    assert sum(r.startswith("usage:") for r in conflict.rows) == 6
    assert conflict.signal == "risk"
    # N-006 is dated 2026-09-18, inside the recent window, so no timing caveat.
    assert conflict.text.endswith(
        "This conflicts with the data: measured STREAM usage changed -22.6% year on year "
        "over the last three complete months (Aug-Oct 2026 versus Aug-Oct 2025)."
    )
    assert result.data["checked"][0]["note_predates_window"] is False
    assert any(g.code == "source_conflict" for g in result.gaps)


def test_note_older_than_the_window_keeps_its_verdict_with_a_caveat(ds):
    # N-004 is dated 2026-03-04; the measured window starts in Aug 2026.
    result = check_claims(ds, "C002")
    fact = next(f for f in result.facts if f.topic == "claim_confirmed")
    assert fact.text.endswith(
        "The data agrees: measured STREAM usage changed +25.2% year on year over the last "
        "three complete months (Aug-Oct 2026 versus Aug-Oct 2025); the note predates this "
        "period."
    )
    assert result.data["checked"] == [
        {"note_id": "N-004", "product_id": "STREAM", "claimed": "up",
         "yoy_pct": result.data["checked"][0]["yoy_pct"], "verdict": "consistent",
         "note_predates_window": True}
    ]


def test_claim_about_a_product_without_usage_is_not_judged(ds):
    # C001's note mentions interest in more streaming; that is intent, not a trend.
    result = check_claims(ds, "C001")
    assert not [f for f in result.facts if f.topic == "source_conflict"]


def test_client_without_notes_has_nothing_to_check(ds):
    result = check_claims(ds, "C004")
    assert result.facts == [] and result.data["checked"] == []

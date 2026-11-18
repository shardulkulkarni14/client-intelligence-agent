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
    assert any(g.code == "source_conflict" for g in result.gaps)


def test_claim_about_a_product_without_usage_is_not_judged(ds):
    # C001's note mentions interest in more streaming; that is intent, not a trend.
    result = check_claims(ds, "C001")
    assert not [f for f in result.facts if f.topic == "source_conflict"]


def test_client_without_notes_has_nothing_to_check(ds):
    result = check_claims(ds, "C004")
    assert result.status == "no_data" and result.facts == []

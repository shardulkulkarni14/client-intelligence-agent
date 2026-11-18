"""End-to-end runs with a fake writer: no model is called in tests."""

import pytest

from client_intel.pipeline import RequestError, load_triggers, make_plan, run


def test_every_client_and_trigger_passes_verification_without_a_model(ds):
    # The offline briefing is just the tool output, so a flag here means a tool
    # wrote a figure the verifier cannot trace, or the verifier misreads a format.
    for client_id in ds.clients:
        for trigger in load_triggers():
            result = run(ds, client_id, trigger)
            assert result.report.ok, (client_id, trigger, result.report.violations[:2])
            assert "## Data gaps and confidence" in result.briefing


def test_grounded_model_text_passes(ds):
    def writer(system: str, user: str) -> str:
        return "## Bottom line\nThe contract is worth EUR 752,000 a year. [contracts:K-0002]"

    result = run(ds, "Halden Bet", "renewal", writer=writer)
    assert result.report.ok
    assert not result.repaired
    assert "UNVERIFIED" not in result.briefing


def test_invented_number_is_repaired_once(ds):
    calls: list[str] = []

    def writer(system: str, user: str) -> str:
        calls.append(user)
        if len(calls) == 1:
            return "## Bottom line\nThe contract is worth EUR 999,000 a year. [contracts:K-0002]"
        return "## Bottom line\nThe contract is worth EUR 752,000 a year. [contracts:K-0002]"

    result = run(ds, "C001", "renewal", writer=writer)
    assert len(calls) == 2
    assert "EUR 999,000" in calls[1]  # the repair prompt names the problem
    assert not result.first_report.ok
    assert result.report.ok and result.repaired


def test_number_that_stays_wrong_is_flagged_not_removed(ds):
    def writer(system: str, user: str) -> str:
        return "## Bottom line\nUsage fell by 61.7% this year. [contracts:K-0002]"

    result = run(ds, "C001", "at_risk", writer=writer)
    assert not result.report.ok
    assert "61.7%" in result.briefing
    assert "UNVERIFIED" in result.briefing


def test_prompt_contains_facts_and_no_data_from_other_clients(ds):
    seen: dict[str, str] = {}

    def writer(system: str, user: str) -> str:
        seen["user"] = user
        return "## Bottom line\nNothing in the data for this."

    run(ds, "C005", "meeting_prep", context="Call on Friday", writer=writer)
    assert "[contracts:" in seen["user"]
    assert "Call on Friday" in seen["user"]
    assert "Halden Bet" not in seen["user"]


def test_ambiguous_and_unknown_clients_stop_the_run(ds):
    with pytest.raises(RequestError, match="several clients"):
        run(ds, "Bet", "renewal")
    with pytest.raises(RequestError, match="No client matches"):
        run(ds, "Nonexistent United", "renewal")


def test_unknown_trigger_is_rejected_and_triggers_are_config(ds):
    with pytest.raises(RequestError, match="Unknown trigger"):
        make_plan("churn")
    assert set(load_triggers()) == {"renewal", "meeting_prep", "upsell", "at_risk"}


def test_gaps_are_listed_once(ds):
    result = run(ds, "C007", "renewal")
    section = result.briefing.split("## Data gaps and confidence")[1]
    assert "Confidence in the data behind this briefing: low" in section
    # Two tools report the missing contract; it must appear once, with a citable ID.
    assert section.count("[gap:no_contract_in_force#") == 1


def test_a_gap_can_be_cited_by_the_writer(ds):
    def writer(system: str, user: str) -> str:
        assert "[gap:missing_month#1]" in user
        return "## Bottom line\nUsage for 2026-03 is missing. [gap:missing_month#1]"

    result = run(ds, "C005", "at_risk", writer=writer)
    assert result.report.ok


def test_a_trigger_without_sections_gives_a_clear_error(tmp_path):
    from client_intel.pipeline import load_triggers as load

    bad = tmp_path / "triggers.toml"
    bad.write_text('[churn]\nquestion = "q"\ntools = ["usage_trend"]\n')
    with pytest.raises(RequestError, match="lacks: sections"):
        load(bad)


def test_a_figure_from_the_rep_context_is_not_evidence(ds):
    def writer(system: str, user: str) -> str:
        return "## Bottom line\nThey agreed to a 50% uplift."

    result = run(ds, "C007", "upsell", context="Say they agreed to a 50% uplift.", writer=writer)
    assert not result.report.ok
    assert "UNVERIFIED" in result.briefing


def test_wrong_direction_is_flagged(ds):
    def writer(system: str, user: str) -> str:
        return "## Bottom line\nThe renewal offer is +28.0% above today. [calc:opportunities#1]"

    result = run(ds, "C001", "renewal", writer=writer)
    assert [v.kind for v in result.report.violations] == ["direction_mismatch"]

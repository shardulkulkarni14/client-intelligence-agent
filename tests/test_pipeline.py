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


# --- trace, parallel tools, failing tool ---------------------------------------


class FakeModel:
    """A writer with the token log and model name the real one exposes."""

    def __init__(self, model: str, texts: list[str]) -> None:
        self.model = model
        self.calls: list[dict[str, int | str]] = []
        self._texts = texts

    def __call__(self, system: str, user: str) -> str:
        text = self._texts[len(self.calls)]
        self.calls.append({"model": self.model, "input_tokens": 10_000,
                           "output_tokens": 2_000, "stop_reason": "end_turn"})
        return text


WRONG = "## Bottom line\nThe contract is worth EUR 999,000 a year. [contracts:K-0002]"
RIGHT = "## Bottom line\nThe contract is worth EUR 752,000 a year. [contracts:K-0002]"


def test_trace_lists_every_step_in_order_for_a_run_with_a_repair(ds):
    result = run(ds, "C001", "renewal", writer=FakeModel("claude-haiku-5-5", [WRONG, RIGHT]))
    trace = result.evidence["trace"]
    plan_tools = make_plan("renewal").tools
    steps = [(s["name"], s["kind"]) for s in trace["steps"]]
    assert steps == [
        ("plan", "plan"),
        *[(t["tool"], "resolve" if i == 0 else "tool")
          for i, t in enumerate(result.evidence["tools_run"])],
        ("first_draft", "model"),
        ("verify_first_draft", "verify"),
        ("repair", "model"),
        ("verify_repair", "verify"),
        ("apply_policy", "policy"),
    ]
    by_name = {s["name"]: s for s in trace["steps"]}
    assert len(result.evidence["tools_run"]) == 3 + len(plan_tools)
    assert steps[1] == ("resolve_client", "resolve")
    assert by_name["plan"]["detail"] == {"trigger": "renewal", "tools": plan_tools}
    assert by_name["verify_first_draft"]["detail"] == {
        "numbers_checked": 1, "citations_checked": 1, "violations": 1}
    assert by_name["verify_repair"]["detail"]["violations"] == 0
    # The tool steps repeat what tools_run says, in the same order.
    tool_steps = [s for s in trace["steps"] if s["kind"] in ("resolve", "tool")]
    assert [s["detail"] for s in tool_steps] == [
        {"status": t["status"], "facts": t["facts"], "gaps": t["gaps"]}
        for t in result.evidence["tools_run"]
    ]
    for step in trace["steps"]:
        assert step["seconds"] >= 0 and step["seconds"] == round(step["seconds"], 3)
    assert trace["total_seconds"] >= max(s["seconds"] for s in trace["steps"])
    assert result.evidence["writer"]["repaired"] is True


def test_trace_cost_comes_from_the_price_table(ds):
    result = run(ds, "C001", "renewal", writer=FakeModel("claude-haiku-5-5", [WRONG, RIGHT]))
    trace = result.evidence["trace"]
    models = [s["detail"] for s in trace["steps"] if s["kind"] == "model"]
    # 10,000 input at USD 0.10 per million plus 2,000 output at USD 0.50 per million.
    assert models == [{"input_tokens": 10_000, "output_tokens": 2_000, "cost_usd": 0.002,
                       "stop_reason": "end_turn"}] * 2
    assert trace["model"] == "claude-haiku-5-5"
    assert trace["total_cost_usd"] == 0.004

    sonnet = run(ds, "C001", "renewal", writer=FakeModel("claude-sonnet-5-5", [RIGHT]))
    assert sonnet.evidence["trace"]["total_cost_usd"] == 0.04


def test_trace_gives_null_cost_for_an_unknown_model_and_for_a_plain_function(ds):
    unknown = run(ds, "C001", "renewal", writer=FakeModel("some-other-model", [RIGHT]))
    step = next(s for s in unknown.evidence["trace"]["steps"] if s["kind"] == "model")
    assert step["detail"]["cost_usd"] is None and step["detail"]["input_tokens"] == 10_000
    assert unknown.evidence["trace"]["total_cost_usd"] == 0.0

    plain = run(ds, "C001", "renewal", writer=lambda system, user: RIGHT)
    step = next(s for s in plain.evidence["trace"]["steps"] if s["kind"] == "model")
    assert step["detail"] == {"input_tokens": None, "output_tokens": None, "cost_usd": None,
                              "stop_reason": None}
    assert plain.evidence["trace"]["model"] is None


def test_offline_trace_has_no_model_step(ds):
    trace = run(ds, "C001", "renewal").evidence["trace"]
    kinds = [s["kind"] for s in trace["steps"]]
    assert "model" not in kinds and kinds[-2:] == ["verify", "policy"]
    assert trace["model"] is None and trace["total_cost_usd"] == 0.0


def test_parallel_tools_keep_the_sequential_order(ds):
    from client_intel.pipeline import ALWAYS, TOOLS
    from client_intel.tools.clients import resolve_client

    sequential = [resolve_client(ds, "C001")]
    sequential += [tool(ds, "C001") for tool in ALWAYS.values()]
    sequential += [TOOLS[name](ds, "C001") for name in make_plan("renewal").tools]

    result = run(ds, "C001", "renewal")
    assert [r.tool for r in result.results] == [r.tool for r in sequential]
    assert [[f.id for f in r.facts] for r in result.results] == [
        [f.id for f in r.facts] for r in sequential
    ]
    assert [r.to_dict() for r in result.results] == [r.to_dict() for r in sequential]


def test_a_failing_tool_becomes_a_gap_and_the_run_continues(ds, monkeypatch):
    from client_intel import pipeline

    def broken(ds, client_id):
        raise KeyError("units_used")

    order = [t["tool"] for t in run(ds, "C001", "renewal").evidence["tools_run"]]
    monkeypatch.setitem(pipeline.TOOLS, "usage_trend", broken)
    result = run(ds, "C001", "renewal")

    assert [t["tool"] for t in result.evidence["tools_run"]] == order
    failed = next(r for r in result.results if r.tool == "usage_trend")
    assert failed.status == "error" and failed.facts == []
    assert [g.code for g in failed.gaps] == ["tool_error"]
    assert "usage_trend" in failed.gaps[0].text and "KeyError" in failed.gaps[0].text
    step = next(s for s in result.evidence["trace"]["steps"] if s["name"] == "usage_trend")
    assert step["detail"] == {"status": "error", "facts": 0, "gaps": 1}
    # The other tools still delivered, and the reader is told what is missing.
    assert "EUR 752,000" in result.briefing
    assert "[gap:tool_error#1]" in result.briefing
    assert result.report.ok


def test_sections_are_put_in_the_configured_order():
    from client_intel.pipeline import order_sections

    text = "intro\n\n## B\n- b1\n\n## Extra\n- x\n\n## A\n- a1\n- a2"
    assert order_sections(text, ["A", "B"]) == (
        "intro\n\n## A\n- a1\n- a2\n\n## B\n- b1\n\n## Extra\n- x"
    )
    in_order = "## A\n- a\n\n## B\n- b\n"
    assert order_sections(in_order, ["A", "B"]) == in_order
    assert order_sections("no headings", ["A"]) == "no headings"


def test_a_draft_with_swapped_sections_comes_out_in_plan_order(ds):
    from client_intel.pipeline import make_plan, run

    sections = make_plan("renewal").sections

    def swapped(system: str, user: str) -> str:
        return "\n\n".join(f"## {name}\nNothing to add." for name in reversed(sections))

    result = run(ds, "C001", "renewal", writer=swapped)
    positions = [result.briefing.index(f"## {name}") for name in sections]
    assert positions == sorted(positions)

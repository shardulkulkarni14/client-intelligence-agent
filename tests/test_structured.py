"""Structured mode: the model selects facts and comments; code writes the figures."""

from __future__ import annotations

import json

import pytest

from client_intel.evidence import Fact
from client_intel.pipeline import RequestError, make_plan, run
from client_intel.structured import EMPTY_SECTION, parse, render

SECTIONS = ["Bottom line", "Usage"]
FACTS = {
    "calc:usage_trend#1": Fact(
        id="calc:usage_trend#1",
        text="ODDS_LIVE (In-play Odds Feed): a change of -40.0% year on year.",
        kind="calc",
    ),
    "note:N-001": Fact(id="note:N-001", text='The client said "up 10%".', kind="reported"),
}


def doc(*sections: tuple[str, list[dict]]) -> str:
    return json.dumps({"sections": [{"heading": h, "items": items} for h, items in sections]})


def test_parse_tolerates_a_code_fence_and_rejects_prose():
    assert parse('```json\n{"sections": []}\n```') == {"sections": []}
    assert parse("Here is the briefing.") is None
    assert parse('{"other": 1}') is None


def test_figures_come_from_the_fact_sentence_not_from_the_model():
    out = render(doc(("Usage", [{"say": "The in-play feed is the concern.",
                                 "facts": ["calc:usage_trend#1"], "show": True}])),
                 SECTIONS, FACTS, "")
    assert out.problems == []
    assert out.body == (
        f"## Bottom line\n\n{EMPTY_SECTION}\n\n## Usage\n\n"
        "- The in-play feed is the concern. ODDS_LIVE (In-play Odds Feed): a change of "
        "-40.0% year on year. [calc:usage_trend#1]"
    )


def test_show_false_prints_the_comment_and_the_citation_only():
    out = render(doc(("Usage", [{"say": "Usage is falling.", "facts": ["calc:usage_trend#1"],
                                 "show": False}])), SECTIONS, FACTS, "")
    assert "- Usage is falling. [calc:usage_trend#1]" in out.body
    assert "-40.0%" not in out.body


def test_a_figure_in_the_models_own_words_is_a_problem():
    out = render(doc(("Usage", [{"say": "Streaming fell 40.0% this year.",
                                 "facts": ["calc:usage_trend#1"], "show": False}])),
                 SECTIONS, FACTS, "")
    assert [p.kind for p in out.problems] == ["figure_in_own_words"]


def test_unknown_fact_ids_are_problems_and_are_not_printed():
    out = render(doc(("Usage", [{"say": "See this.", "facts": ["calc:nope#9"]}])),
                 SECTIONS, FACTS, "")
    assert [p.kind for p in out.problems] == ["unknown_fact_id"]
    assert "calc:nope#9" not in out.body


def test_reported_facts_are_labelled_and_sections_follow_the_plan_order():
    out = render(doc(("Usage", [{"say": "", "facts": ["note:N-001"]}]),
                     ("Bottom line", [{"say": "Unclear."}]),
                     ("Invented section", [{"say": "Ignored."}])), SECTIONS, FACTS, "")
    assert out.body.index("## Bottom line") < out.body.index("## Usage")
    assert '- Reported: The client said "up 10%". [note:N-001]' in out.body
    assert "Invented" not in out.body


def _writer(trigger: str, items: list[dict]):
    sections = make_plan(trigger).sections

    def write(system: str, user: str) -> str:
        return doc(*[(name, items if i == 1 else []) for i, name in enumerate(sections)])

    return write


def test_run_in_structured_mode_renders_the_tool_sentence(ds):
    result = run(ds, "C001", "renewal", mode="structured", writer=_writer(
        "renewal", [{"say": "This is the contract.", "facts": ["contracts:K-0002"]}]))
    assert result.report.ok
    assert "EUR 752,000" in result.briefing
    assert result.evidence["writer"]["mode"] == "structured"
    assert result.evidence["writer"]["fallback"] is False
    assert result.evidence["writer"]["structured"]["sections"][1]["items"][0]["facts"] == [
        "contracts:K-0002"
    ]


def test_run_flags_a_figure_the_model_wrote_itself(ds):
    result = run(ds, "C001", "renewal", mode="structured", writer=_writer(
        "renewal", [{"say": "Streaming revenue fell 40.0%.", "facts": ["contracts:K-0002"],
                     "show": False}]))
    assert not result.report.ok
    assert "UNVERIFIED" in result.briefing


def test_unreadable_output_twice_falls_back_to_the_facts_only_briefing(ds):
    result = run(ds, "C001", "renewal", mode="structured",
                 writer=lambda system, user: "I cannot do that.")
    assert result.evidence["writer"]["fallback"] is True
    assert "could not be read" in result.briefing
    assert "EUR 752,000" in result.briefing


def test_unknown_mode_is_rejected(ds):
    with pytest.raises(RequestError, match="Unknown mode"):
        run(ds, "C001", "renewal", mode="poetry")

import pytest

from client_intel.evidence import CALC, DATA, REPORTED, Fact
from client_intel.verify import (
    NumberToken,
    VerificationReport,
    Violation,
    apply_policy,
    extract_citations,
    extract_numbers,
    repair_instructions,
    verify,
)

K = "contracts:K-0002"
TREND = "calc:usage_trend#3"
UTIL = "calc:utilisation#1"
NOTE = "note:N-003"
TICKET = "ticket:T-0123"


@pytest.fixture
def facts() -> dict[str, Fact]:
    items = [
        Fact(
            id=K,
            text="Contract K-0002 for ODDS_LIVE has annual value EUR 752,000 and ends 2026-12-31.",
            rows=[K],
            kind=DATA,
        ),
        Fact(
            id=TREND,
            text="API calls changed -28.0% from 11,988 to 8,631 between 2026-07 and 2026-10.",
            rows=["usage:U-00421", "usage:U-00422"],
            kind=CALC,
        ),
        Fact(
            id=UTIL,
            text="Utilisation is 45.5% of the committed volume.",
            rows=["usage:U-00422"],
            kind=CALC,
        ),
        Fact(
            id=NOTE,
            text="Client said a competitor quoted EUR 600,000 for 3 years.",
            rows=[NOTE],
            kind=REPORTED,
        ),
        Fact(
            id=TICKET,
            text="Ticket T-0123 (P1) has been open for 14 days.",
            rows=[TICKET],
            kind=DATA,
        ),
    ]
    return {f.id: f for f in items}


def kinds(report: VerificationReport) -> list[tuple[int, str, str]]:
    return [(v.line_no, v.kind, v.token) for v in report.violations]


def test_clean_briefing_passes(facts):
    briefing = "\n".join(
        [
            "# Briefing for C001",
            "",
            f"- The contract is worth EUR 752,000 and ends 2026-12-31 [{K}].",
            f"- API calls fell 28.0% to 8,631 [{TREND}].",
            f"- Ticket T-0123 (P1) has been open for 14 days [{TICKET}].",
        ]
    )
    report = verify(briefing, facts)
    assert report.ok is True
    assert report.violations == []
    assert report.numbers_checked == 5
    assert report.citations_checked == 3


def test_invented_number_is_flagged(facts):
    line = f"The contract is worth EUR 800,000 [{K}]."
    report = verify("Intro.\n" + line, facts)
    assert report.ok is False
    assert report.violations == [
        Violation(
            line_no=2,
            line=line,
            kind="number_not_in_cited_evidence",
            token="EUR 800,000",
            detail="EUR 800,000 is not in the evidence cited on this line",
        )
    ]


def test_number_cited_to_the_wrong_fact_is_flagged_and_points_to_the_right_one(facts):
    report = verify(f"Utilisation is 45.5% [{K}].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", "45.5%")]
    assert report.violations[0].detail.endswith(f"it does appear in {UTIL}")


def test_unknown_citation(facts):
    report = verify("The contract renews soon [contracts:K-9999].", facts)
    assert kinds(report) == [(1, "unknown_citation", "contracts:K-9999")]
    assert report.citations_checked == 1
    assert report.numbers_checked == 0


def test_number_next_to_unknown_citation_is_also_unsupported(facts):
    report = verify("Value is EUR 752,000 [contracts:K-9999].", facts)
    assert kinds(report) == [
        (1, "unknown_citation", "contracts:K-9999"),
        (1, "number_not_in_cited_evidence", "EUR 752,000"),
    ]


def test_number_without_citation_does_not_inherit_from_the_previous_line(facts):
    briefing = f"The contract is worth EUR 752,000 [{K}].\nUsage fell to 8,631 calls."
    report = verify(briefing, facts)
    assert kinds(report) == [(2, "number_without_citation", "8,631")]


def test_heading_numbers_are_checked_like_any_line(facts):
    report = verify("## Renewal outlook 2027\n\n### 3 things to know", facts)
    assert kinds(report) == [
        (1, "number_without_citation", "2027"),
        (3, "number_without_citation", "3"),
    ]
    assert verify(f"## Worth EUR 752,000 [{K}]", facts).ok is True
    assert kinds(verify(f"## Worth EUR 800,000 [{K}]", facts)) == [
        (1, "number_not_in_cited_evidence", "EUR 800,000")
    ]


def test_allowed_headings_are_exempt(facts):
    briefing = "## Next 30 days\n\n### Top 3 risks"
    report = verify(briefing, facts, allowed_headings=["Next 30 days"])
    assert kinds(report) == [(3, "number_without_citation", "3")]
    assert report.numbers_checked == 1
    both = verify(briefing, facts, allowed_headings=("next 30 days", "## Top 3 risks"))
    assert both.ok is True
    assert both.numbers_checked == 0
    # the exemption is for the whole heading text, not for a heading that contains it
    assert kinds(verify("## Next 30 days: 99 calls", facts, allowed_headings=["Next 30 days"])) == [
        (1, "number_without_citation", "30"),
        (1, "number_without_citation", "99"),
    ]


def test_ids_priorities_and_product_ids_are_not_numbers():
    text = "Ticket T-0123 is P1 for client C001 on ODDS_LIVE under K-0002, see U-00422 and O-0001."
    assert extract_numbers(text) == []
    assert extract_numbers("Note N-003 lists P4 and P2 items.") == []


def test_numbers_inside_citations_are_not_numbers(facts):
    assert extract_numbers(f"Calls fell [{TREND}][usage:U-00422].") == []
    assert verify(f"Calls fell [{TREND}].", facts).numbers_checked == 0


def test_extract_numbers_types_and_values():
    text = "EUR 752,000 or 8,631 calls, -28.0% by 2026-12-31 (2026-10), 12.5 percent, 752k"
    assert extract_numbers(text) == [
        NumberToken("EUR 752,000", "752000", "eur"),
        NumberToken("8,631", "8631", "number"),
        NumberToken("28.0%", "28.0", "percent", "-"),
        NumberToken("2026-12-31", "2026-12-31", "date"),
        NumberToken("2026-10", "2026-10", "month"),
        NumberToken("12.5 percent", "12.5", "percent"),
        NumberToken("752k", "752", "abbreviated"),
    ]


@pytest.mark.parametrize(
    "written", ["EUR 752,000", "€752,000", "752,000 EUR", "EUR 752000", "752,000", "€ 752,000"]
)
def test_eur_forms_all_match(facts, written):
    report = verify(f"Annual value is {written} [{K}].", facts)
    assert report.ok is True
    assert report.numbers_checked == 1


@pytest.mark.parametrize("written", ["EUR 752k", "752k", "€0.75m", "EUR 0.752 million", "752K EUR"])
def test_abbreviated_figures_are_rejected(facts, written):
    report = verify(f"Annual value is {written} [{K}].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", written)]
    assert "abbreviated figures are not accepted" in report.violations[0].detail


def test_money_must_be_money_in_the_evidence(facts):
    report = verify(f"Usage is worth EUR 8,631 [{TREND}].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", "EUR 8,631")]


@pytest.mark.parametrize(
    "written",
    ["down 28.0%", "-28.0%", "down 28%", "down 28.0 percent", "down -28.0%",
     "a change of -28.0%", "−28.0 %"],
)
def test_percent_matches_at_written_precision_with_the_right_direction(facts, written):
    assert verify(f"API calls moved {written} [{TREND}].", facts).ok is True


@pytest.mark.parametrize(
    ("line", "token", "detail"),
    [
        (
            "API calls moved +28.0%",
            "+28.0%",
            "+28.0% has the wrong sign or direction; the cited evidence says -28.0%",
        ),
        (
            "API calls are up 28.0%",
            "28.0%",
            "'up' 28.0% has the wrong sign or direction; the cited evidence says -28.0%",
        ),
        (
            "API calls rose by a strong 28%",
            "28%",
            "'rose' 28% has the wrong sign or direction; the cited evidence says -28.0%",
        ),
        (
            "API calls are 28.0% higher than in July",
            "28.0%",
            "'higher' 28.0% has the wrong sign or direction; the cited evidence says -28.0%",
        ),
        (
            "Usage growth of 28.0 percent",
            "28.0 percent",
            "'growth' 28.0 percent has the wrong sign or direction; "
            "the cited evidence says -28.0%",
        ),
    ],
)
def test_direction_mismatch(facts, line, token, detail):
    report = verify(f"{line} [{TREND}].", facts)
    assert kinds(report) == [(1, "direction_mismatch", token)]
    assert report.violations[0].detail == detail


@pytest.mark.parametrize(
    "line",
    [
        "API calls fell 28.0%",
        "API calls are 28.0% lower than in July",
        "API calls are 28.0% below the July level",
        "API calls dropped, by our count, 28.0%",
        "A decline of 28.0% in API calls",
        # the nearest direction word decides
        "From a higher base, calls are down 28.0%",
    ],
)
def test_direction_agrees_or_is_not_stated(facts, line):
    assert verify(f"{line} [{TREND}].", facts).ok is True


@pytest.mark.parametrize(
    "line",
    [
        "API calls moved 28.0%",
        "API calls surprised everyone with 28.0%",
        # a direction word in another sentence does not count
        "Revenue is up. API calls moved 28.0%",
        # too far away: more than 5 words before
        "Up is not the word for what happened here: 28.0%",
        "API calls changed 28.0% and nothing else of note went up",
        # a ceiling, not a rise
        "A change of up to 28.0%",
    ],
)
def test_a_change_without_sign_or_direction_word_is_flagged(facts, line):
    # The evidence says -28.0%. A sentence that gives neither the sign nor a known
    # direction word cannot be checked, and the word list can never be complete.
    report = verify(f"{line} [{TREND}].", facts)
    assert [v.kind for v in report.violations] == ["direction_mismatch"]
    assert "copy it as in the evidence: -28.0%" in report.violations[0].detail


@pytest.mark.parametrize("word", ["surged", "climbed", "jumped"])
def test_more_rise_words_are_caught_against_a_fall(facts, word):
    report = verify(f"API calls {word} 28.0% [{TREND}].", facts)
    assert [v.kind for v in report.violations] == ["direction_mismatch"]


def test_direction_against_positive_and_unsigned_evidence(facts):
    facts["calc:g#1"] = Fact(id="calc:g#1", text="Revenue changed +12.5% year on year.", kind=CALC)
    assert verify("Revenue is up 12.5% [calc:g#1].", facts).ok is True
    assert verify("Revenue moved +12.5% [calc:g#1].", facts).ok is True
    assert kinds(verify("Revenue fell 12.5% [calc:g#1].", facts)) == [
        (1, "direction_mismatch", "12.5%")
    ]
    assert kinds(verify("Revenue moved -12.5% [calc:g#1].", facts)) == [
        (1, "direction_mismatch", "-12.5%")
    ]
    # an unsigned evidence figure is a level: a minus sign is wrong, a direction
    # word next to it cannot be judged
    assert kinds(verify(f"Utilisation is -45.5% [{UTIL}].", facts)) == [
        (1, "direction_mismatch", "-45.5%")
    ]
    assert verify(f"Utilisation is +45.5% [{UTIL}].", facts).ok is True
    assert verify(f"Utilisation is down at 45.5% [{UTIL}].", facts).ok is True


def test_same_value_with_both_signs_in_cited_facts_is_accepted(facts):
    facts["calc:g#2"] = Fact(id="calc:g#2", text="Widget views changed +28.0%.", kind=CALC)
    for written in ("up 28.0%", "down 28.0%", "+28.0%", "-28.0%"):
        assert verify(f"The move was {written} [{TREND}][calc:g#2].", facts).ok is True
    assert kinds(verify("The move was up 28.0% [calc:g#2].", facts)) == []
    assert kinds(verify(f"The move was up 28.0% [{TREND}].", facts)) == [
        (1, "direction_mismatch", "28.0%")
    ]


def test_sign_is_read_only_directly_before_the_figure():
    def signs(text: str) -> list[str]:
        return [t.sign for t in extract_numbers(text)]

    assert signs("+28.0% and -3 and −4.5% and EUR -5,000 and -€6") == ["+", "-", "-", "-", "-"]
    assert signs("- 28.0% is a bullet, 10-20% a range, mid-50 a word") == ["", "", "", ""]


@pytest.mark.parametrize(
    ("written", "cite", "token"),
    [
        ("28.1%", TREND, "28.1%"),
        ("29%", TREND, "29%"),
        ("45%", UTIL, "45%"),
        ("8,631%", TREND, "8,631%"),
    ],
)
def test_percent_mismatch(facts, written, cite, token):
    report = verify(f"The figure is {written} [{cite}].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", token)]


def test_percent_rounds_half_up_to_written_precision(facts):
    assert verify(f"Utilisation is about 46% [{UTIL}].", facts).ok is True


def test_iso_date_must_match_exactly(facts):
    assert verify(f"The contract ends 2026-12-31 [{K}].", facts).ok is True
    report = verify(f"The contract ends 2026-12-30 [{K}].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", "2026-12-30")]


def test_month_token_and_year_with_month_name(facts):
    assert verify(f"Lowest month was 2026-10 [{TREND}].", facts).ok is True
    assert verify(f"The contract runs to 2026-12 [{K}].", facts).ok is True
    assert verify(f"Usage dropped by Oct 2026 [{TREND}].", facts).ok is True
    assert kinds(verify(f"Lowest month was 2026-09 [{TREND}].", facts)) == [
        (1, "number_not_in_cited_evidence", "2026-09")
    ]
    assert kinds(verify(f"Usage dropped by Oct 2025 [{TREND}].", facts)) == [
        (1, "number_not_in_cited_evidence", "2025")
    ]


def test_extract_citations_forms():
    assert extract_citations(
        f"A [{K}][{TREND}] b [{UTIL}; {NOTE}] c [{TICKET}, usage:U-00422]"
    ) == [
        K,
        TREND,
        UTIL,
        NOTE,
        TICKET,
        "usage:U-00422",
    ]
    assert extract_citations("A [link](http://x.test) and **[UNVERIFIED: x]** and [1]") == []


@pytest.mark.parametrize(
    "cites", [f"[{K}][{TREND}]", f"[{K}; {TREND}]", f"[{K}, {TREND}]", f"[{TREND}] [{K}]"]
)
def test_several_citations_on_one_line(facts, cites):
    report = verify(f"EUR 752,000 a year while calls fell to 8,631 {cites}.", facts)
    assert report.ok is True
    assert report.numbers_checked == 2
    assert report.citations_checked == 2


def test_source_row_is_a_valid_citation_but_lends_no_calculated_figures(facts):
    report = verify("Calls were 8,631 at 45.5% utilisation [usage:U-00422].", facts)
    assert kinds(report) == [
        (1, "number_not_in_cited_evidence", "8,631"),
        (1, "number_not_in_cited_evidence", "45.5%"),
    ]
    assert report.citations_checked == 1
    assert report.violations[0].detail == (
        "8,631 is not in the evidence cited on this line; a cited source row does not "
        f"carry figures computed from it, cite [{TREND}] instead"
    )
    assert report.violations[1].detail == (
        "45.5% is not in the evidence cited on this line; a cited source row does not "
        f"carry figures computed from it, cite [{UTIL}] instead"
    )
    # U-00421 feeds the trend only: the hint must not name the utilisation fact
    other = verify("Utilisation was 45.5% [usage:U-00421].", facts)
    assert kinds(other) == [(1, "number_not_in_cited_evidence", "45.5%")]
    assert other.violations[0].detail == (
        f"45.5% is not in the evidence cited on this line; it does appear in {UTIL}"
    )
    # a row citation without numbers stays valid
    assert verify("October usage is the low point [usage:U-00422].", facts).ok is True
    # citing the calc fact next to the row is the fix
    assert verify(f"Calls were 8,631 [usage:U-00422][{TREND}].", facts).ok is True


def test_row_with_its_own_fact_supports_only_that_fact(facts):
    # the review's case: a ticket row feeds a CSAT average; an invented average
    # cited to the ticket must not pass because the ticket appears in some rows
    facts["calc:support#1"] = Fact(
        id="calc:support#1",
        text="Average CSAT is 1.3 out of 5, from 4 rated tickets.",
        rows=[TICKET, "ticket:T-0284"],
        kind=CALC,
    )
    report = verify("Average CSAT is 7 out of 5 [ticket:T-0284].", facts)
    assert kinds(report) == [
        (1, "number_not_in_cited_evidence", "7"),
        (1, "number_not_in_cited_evidence", "5"),
    ]
    assert report.violations[0].detail == "7 is not in the evidence cited on this line"
    assert report.violations[1].detail.endswith("cite [calc:support#1] instead")
    # TICKET has a fact of its own (14 days) and does not lend the average either
    assert kinds(verify(f"Average CSAT is 1.3 after 14 days [{TICKET}].", facts)) == [
        (1, "number_not_in_cited_evidence", "1.3")
    ]
    assert verify("Average CSAT is 1.3 out of 5 [calc:support#1].", facts).ok is True


def test_reported_number_needs_a_marker(facts):
    report = verify(f"A competitor offer of EUR 600,000 is on the table [{NOTE}].", facts)
    assert kinds(report) == [(1, "number_only_reported", "EUR 600,000")]
    assert NOTE in report.violations[0].detail


@pytest.mark.parametrize(
    "line",
    [
        f"The client said a competitor quoted EUR 600,000 [{NOTE}].",
        f"According to the meeting note, the rival price is EUR 600,000 [{NOTE}].",
        f"Reported competitor price: EUR 600,000 [{NOTE}].",
        f'Note: "competitor at EUR 600,000" [{NOTE}].',
    ],
)
def test_reported_number_with_marker_passes(facts, line):
    assert verify(line, facts).ok is True


def test_number_also_backed_by_measured_fact_needs_no_marker(facts):
    facts["calc:x#1"] = Fact(id="calc:x#1", text="The offer is EUR 600,000.", kind=CALC)
    assert verify(f"The offer is EUR 600,000 [{NOTE}][calc:x#1].", facts).ok is True


def test_allowed_text(facts):
    line = "Briefing for C001 as of 2026-11-18, renewal in 60 days."
    assert kinds(verify(line, facts)) == [
        (1, "number_without_citation", "2026-11-18"),
        (1, "number_without_citation", "60"),
    ]
    report = verify(line, facts, allowed_text="C001 as of 2026-11-18; renewal in 60 days")
    assert report.ok is True
    assert report.numbers_checked == 2
    assert verify("Outlook for Nov 2026.", facts, allowed_text="2026-11-18").ok is True


CONTEXT = "They told me a rival offered EUR 550,000 and 20% off."


def test_context_number_needs_attribution(facts):
    report = verify("A rival offer of EUR 550,000 is on the table.", facts, context_text=CONTEXT)
    assert kinds(report) == [(1, "number_without_citation", "EUR 550,000")]
    assert report.violations[0].detail == (
        "EUR 550,000 is on a line with no citation; it appears only in the rep's context, "
        "so say that the rep stated it"
    )
    cited = verify(f"A rival offer of EUR 550,000 exists [{K}].", facts, context_text=CONTEXT)
    assert kinds(cited) == [(1, "number_not_in_cited_evidence", "EUR 550,000")]
    assert cited.violations[0].detail == (
        "EUR 550,000 is not in the evidence cited on this line; it appears only in the "
        "rep's context, so say that the rep stated it"
    )


@pytest.mark.parametrize(
    "line",
    [
        "The rep heard of a rival offer of EUR 550,000.",
        "Context from the account owner: rival at EUR 550,000 with 20% off.",
        "A rival reportedly offered EUR 550,000.",
        'The client spoke of "EUR 550,000".',
        f"According to the rep the rival is at EUR 550,000, against EUR 752,000 today [{K}].",
    ],
)
def test_context_number_with_attribution_passes(facts, line):
    assert verify(line, facts, context_text=CONTEXT).ok is True


def test_context_does_not_cover_other_numbers_or_replace_allowed_text(facts):
    report = verify("The rep heard of a rival offer of EUR 560,000.", facts, context_text=CONTEXT)
    assert kinds(report) == [(1, "number_without_citation", "EUR 560,000")]
    # allowed_text keeps its meaning: no attribution needed
    assert verify("Briefing as of 2026-11-18.", facts, "2026-11-18", context_text=CONTEXT).ok
    # a word that merely contains "rep" is not an attribution
    assert kinds(
        verify("We prepared for EUR 550,000.", facts, context_text=CONTEXT)
    ) == [(1, "number_without_citation", "EUR 550,000")]


def test_uncited_lines_are_counted_not_flagged(facts):
    briefing = "\n".join(
        [
            "## Bottom line",
            "The account is at risk.",
            "",
            f"- The contract is worth EUR 752,000 [{K}].",
            f"- Usage is the main worry [{TREND}].",
            "- Call the client this week.",
            "---",
            "| Metric | Value |",
            "|---|---:|",
            "Renewal in 60 days.",
        ]
    )
    report = verify(briefing, facts)
    # lines 2, 6 and 8; not the heading, the cited lines, the rules or the line with a number
    assert report.uncited_lines == 3
    assert kinds(report) == [(10, "number_without_citation", "60")]
    assert report.to_dict()["uncited_lines"] == 3
    assert verify(f"- Worth EUR 752,000 [{K}].", facts).uncited_lines == 0


def test_apply_policy_states_uncited_lines(facts):
    one = f"The account is at risk.\n- Worth EUR 752,000 [{K}]."
    assert apply_policy(one, verify(one, facts)).endswith(
        "## Verification\n\n"
        "All 1 numbers and 1 citations were matched to the facts cited on their lines. "
        "The check covers figures, their signs and citation IDs; it does not judge the "
        "wording around them.\n\n"
        "1 line carries no figure and no citation; it is interpretation and was not checked.\n"
    )
    two = "The account is at risk.\nCall them.\nUsage fell to 9,999 calls."
    assert apply_policy(two, verify(two, facts)).endswith(
        '- "Usage fell to 9,999 calls.": 9,999 is on a line with no citation '
        "(number_without_citation)\n\n"
        "2 lines carry no figure and no citation; they are interpretation and were not "
        "checked.\n"
    )


def test_verification_section_quotes_the_line_not_its_number(facts):
    long_line = "- " + "The annual value of this contract is, as far as we can tell, " * 2 + (
        f"EUR 800,000 [{K}]."
    )
    out = apply_policy(long_line, verify(long_line, facts))
    section = out.split("## Verification\n")[1]
    assert "Line 1" not in section
    quoted = long_line[:80].rstrip()
    assert len(long_line) > 80
    assert section.splitlines()[3] == (
        f'- "{quoted}...": EUR 800,000 is not in the evidence cited on this line '
        "(number_not_in_cited_evidence)"
    )


def test_direction_mismatch_is_flagged_in_the_text(facts):
    line = f"- API calls are up 28.0% [{TREND}]."
    out = apply_policy(line, verify(line, facts))
    assert out.splitlines()[0] == (
        f"{line} **[UNVERIFIED: 28.0% has the wrong sign or direction]**"
    )
    assert kinds(verify(out.split("## Verification")[0], facts)) == [
        (1, "direction_mismatch", "28.0%")
    ]


def test_table_rows(facts):
    briefing = "\n".join(
        [
            "| Metric | Value | Source |",
            "|---|---:|:--|",
            f"| Annual value | EUR 752,000 | [{K}] |",
            f"| Calls | 8,613 | [{TREND}] |",
            "| Open days | 14 | |",
        ]
    )
    report = verify(briefing, facts)
    assert kinds(report) == [
        (4, "number_not_in_cited_evidence", "8,613"),
        (5, "number_without_citation", "14"),
    ]
    flagged = apply_policy(briefing, report).splitlines()
    assert flagged[3] == (
        f"| Calls | 8,613 | [{TREND}] **[UNVERIFIED: 8,613 not in cited evidence]** |"
    )
    assert flagged[4] == "| Open days | 14 | **[UNVERIFIED: 14 has no citation]** |"


def test_ordered_list_marker_is_ignored(facts):
    briefing = f"1. Annual value is EUR 752,000 [{K}].\n2) Ask about the renewal.\n  3. Follow up."
    report = verify(briefing, facts)
    assert report.ok is True
    assert report.numbers_checked == 1


def test_apply_policy_keeps_text_flags_lines_and_adds_section(facts):
    briefing = f"# Briefing\n\n- Value is EUR 800,000 [{K}].\n- Ends 2026-12-31 [{K}].\n"
    report = verify(briefing, facts)
    out = apply_policy(briefing, report)
    assert out == (
        "# Briefing\n"
        "\n"
        f"- Value is EUR 800,000 [{K}]. **[UNVERIFIED: EUR 800,000 not in cited evidence]**\n"
        f"- Ends 2026-12-31 [{K}].\n"
        "\n"
        "## Verification\n"
        "\n"
        "2 numbers and 2 citations were checked against the evidence; 1 could not be "
        "verified and are marked UNVERIFIED above:\n"
        "\n"
        f'- "- Value is EUR 800,000 [{K}].": EUR 800,000 is not in the evidence cited '
        "on this line (number_not_in_cited_evidence)\n"
    )


def test_apply_policy_clean(facts):
    briefing = f"- Value is EUR 752,000 [{K}]."
    out = apply_policy(briefing, verify(briefing, facts))
    assert out == (
        f"- Value is EUR 752,000 [{K}].\n\n## Verification\n\n"
        "All 1 numbers and 1 citations were matched to the facts cited on their lines. "
        "The check covers figures, their signs and citation IDs; it does not judge the "
        "wording around them.\n"
    )


def test_flagged_output_does_not_add_new_violations(facts):
    briefing = "Usage fell to 9,999 calls.\nSee [contracts:K-9999]."
    report = verify(briefing, facts)
    flagged_body = apply_policy(briefing, report).split("## Verification")[0]
    assert kinds(verify(flagged_body, facts)) == kinds(report)


def test_repair_instructions(facts):
    briefing = f"Fine line [{K}].\nUsage fell to 9,999 calls [{TREND}]."
    report = verify(briefing, facts)
    text = repair_instructions(report)
    assert text.splitlines()[1:] == [
        "- Line 2 (number_not_in_cited_evidence): 9,999 is not in the evidence cited on this line",
        f"  > Usage fell to 9,999 calls [{TREND}].",
    ]
    assert repair_instructions(verify(f"Fine line [{K}].", facts)) == ""


def test_to_dict(facts):
    report = verify("Usage fell to 9,999 calls.", facts)
    assert report.to_dict() == {
        "ok": False,
        "numbers_checked": 1,
        "citations_checked": 0,
        "violations": [
            {
                "line_no": 1,
                "line": "Usage fell to 9,999 calls.",
                "kind": "number_without_citation",
                "token": "9,999",
                "detail": "9,999 is on a line with no citation",
            }
        ],
        "uncited_lines": 0,
    }


def test_citation_with_a_marker_inside_the_bracket_is_still_a_citation():
    assert extract_citations("x [note:N-003, reported].") == ["note:N-003"]
    assert extract_citations("x [ticket:T-0269, client-written].") == ["ticket:T-0269"]
    assert extract_citations("x [reported]") == []
    assert extract_citations("x [UNVERIFIED: 5 is not in note:N-003, check]") == []


def test_unknown_id_with_a_marker_inside_the_bracket_is_flagged(facts):
    report = verify("The client said so [note:N-999, reported].", facts)
    assert [v.kind for v in report.violations] == ["unknown_citation"]


SUBJECTS = {
    "ODDS_LIVE": "In-play Odds Feed",
    "STREAM": "Live Streaming",
    "WIDGETS": "Match Visualisation Widgets",
}
ODDS_TREND = "calc:usage_trend#10"
STREAM_TREND = "calc:usage_trend#11"


@pytest.fixture
def product_facts() -> dict[str, Fact]:
    items = [
        Fact(
            id=ODDS_TREND,
            text="ODDS_LIVE (In-play Odds Feed) API calls changed -40.0% from 2026-07 to 2026-10.",
            rows=["usage:U-00500"],
            kind=CALC,
        ),
        Fact(
            id=STREAM_TREND,
            text="Usage changed +5.0% between 2026-07 and 2026-10.",
            rows=["usage:U-00600", "product:STREAM"],
            kind=CALC,
        ),
    ]
    return {f.id: f for f in items}


def test_wrong_product_by_name_is_flagged(product_facts):
    line = f"Live Streaming usage fell -40.0% [{ODDS_TREND}]."
    report = verify(line, product_facts, subjects=SUBJECTS)
    assert report.violations == [
        Violation(
            line_no=1,
            line=line,
            kind="subject_not_in_cited_evidence",
            token="Live Streaming",
            detail="Live Streaming is named on this line, but no fact cited here is about it",
        )
    ]
    # the full name is matched in any case
    lower = verify(f"live streaming usage fell -40.0% [{ODDS_TREND}].", product_facts,
                   subjects=SUBJECTS)
    assert kinds(lower) == [(1, "subject_not_in_cited_evidence", "live streaming")]


def test_wrong_product_by_id_is_flagged(product_facts):
    report = verify(f"STREAM usage fell -40.0% [{ODDS_TREND}].", product_facts, subjects=SUBJECTS)
    assert kinds(report) == [(1, "subject_not_in_cited_evidence", "STREAM")]
    assert report.violations[0].detail == (
        "STREAM is named on this line, but no fact cited here is about it"
    )
    # an id is a whole token in exact case: the ordinary word is not the product
    assert verify(f"The stream of calls fell -40.0% [{ODDS_TREND}].", product_facts,
                  subjects=SUBJECTS).ok is True
    assert verify(f"UPSTREAM calls fell -40.0% [{ODDS_TREND}].", product_facts,
                  subjects=SUBJECTS).ok is True


def test_right_product_passes(product_facts):
    for line in (
        f"In-play Odds Feed usage fell -40.0% [{ODDS_TREND}].",
        f"ODDS_LIVE usage fell -40.0% [{ODDS_TREND}].",
        # the fact names the product only through its rows
        f"Live Streaming usage rose +5.0% [{STREAM_TREND}].",
        # the product row itself is cited next to the calculation
        f"Widgets (WIDGETS) usage fell -40.0% [{ODDS_TREND}][product:WIDGETS].",
    ):
        facts = dict(product_facts)
        facts["product:WIDGETS"] = Fact(
            id="product:WIDGETS", text="Catalogue entry.", rows=["product:WIDGETS"], kind=DATA
        )
        assert verify(line, facts, subjects=SUBJECTS).ok is True, line


def test_line_naming_two_products_with_facts_for_both_passes(product_facts):
    line = (
        f"In-play Odds Feed fell -40.0% while Live Streaming rose +5.0% "
        f"[{ODDS_TREND}][{STREAM_TREND}]."
    )
    report = verify(line, product_facts, subjects=SUBJECTS)
    assert report.ok is True
    assert report.numbers_checked == 2


def test_second_product_without_a_cited_fact_is_flagged_once(product_facts):
    line = (
        f"ODDS_LIVE fell -40.0%, and Live Streaming (STREAM) fell by the same -40.0% "
        f"[{ODDS_TREND}]."
    )
    report = verify(line, product_facts, subjects=SUBJECTS)
    assert kinds(report) == [(1, "subject_not_in_cited_evidence", "Live Streaming")]


def test_line_without_numbers_is_not_subject_checked(product_facts):
    report = verify(f"Live Streaming usage is falling [{ODDS_TREND}].", product_facts,
                    subjects=SUBJECTS)
    assert report.ok is True
    # nor is a line whose only citation is unknown: that is already a violation
    unknown = verify("Live Streaming usage fell -40.0% [calc:nope#1].", product_facts,
                     subjects=SUBJECTS)
    assert [v.kind for v in unknown.violations] == [
        "unknown_citation",
        "number_not_in_cited_evidence",
    ]


def test_without_subjects_the_wrong_product_still_passes(product_facts):
    line = f"Live Streaming usage fell -40.0% [{ODDS_TREND}]."
    assert verify(line, product_facts).ok is True
    assert verify(line, product_facts, subjects=None).ok is True
    assert verify(line, product_facts, subjects={}).ok is True


def test_subject_violation_is_flagged_in_the_text_and_in_the_repair(product_facts):
    line = f"- Live Streaming usage fell -40.0% [{ODDS_TREND}]."
    report = verify(line, product_facts, subjects=SUBJECTS)
    out = apply_policy(line, report)
    assert out.splitlines()[0] == (
        f"{line} **[UNVERIFIED: Live Streaming is not the subject of the cited evidence]**"
    )
    assert (
        f'- "{line}": Live Streaming is named on this line, but no fact cited here is '
        "about it (subject_not_in_cited_evidence)"
    ) in out
    assert repair_instructions(report).splitlines()[1] == (
        "- Line 1 (subject_not_in_cited_evidence): Live Streaming is named on this line, "
        "but no fact cited here is about it"
    )
    # re-verifying the flagged text does not add a second violation
    assert kinds(verify(out.split("## Verification")[0], product_facts, subjects=SUBJECTS)) == [
        (1, "subject_not_in_cited_evidence", "Live Streaming")
    ]

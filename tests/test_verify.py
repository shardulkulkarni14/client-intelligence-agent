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


def test_heading_with_a_year_is_fine(facts):
    report = verify("## Renewal outlook 2027\n\n### 3 things to know", facts)
    assert report.ok is True
    assert report.numbers_checked == 0


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
        NumberToken("28.0%", "28.0", "percent"),
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


@pytest.mark.parametrize("written", ["down 28.0%", "-28.0%", "28%", "+28.0 %", "28.0 percent"])
def test_percent_matches_ignoring_sign_and_at_written_precision(facts, written):
    assert verify(f"API calls moved {written} [{TREND}].", facts).ok is True


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


def test_citing_a_source_row_of_a_calc_fact(facts):
    assert verify("Calls were 8,631 at 45.5% utilisation [usage:U-00422].", facts).ok is True
    # U-00421 feeds the trend only, not the utilisation figure
    report = verify("Utilisation was 45.5% [usage:U-00421].", facts)
    assert kinds(report) == [(1, "number_not_in_cited_evidence", "45.5%")]


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
        "- Line 3: EUR 800,000 is not in the evidence cited on this line "
        "(number_not_in_cited_evidence)\n"
    )


def test_apply_policy_clean(facts):
    briefing = f"- Value is EUR 752,000 [{K}]."
    out = apply_policy(briefing, verify(briefing, facts))
    assert out == (
        f"- Value is EUR 752,000 [{K}].\n\n## Verification\n\n"
        "All 1 numbers and 1 citations were checked against the evidence.\n"
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
    }

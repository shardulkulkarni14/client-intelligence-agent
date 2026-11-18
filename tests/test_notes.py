from dataclasses import replace

from client_intel.db import Dataset
from client_intel.evidence import CALC, DATA, NO_DATA, OK, REPORTED
from client_intel.tools.notes import (
    MAX_QUOTES_PER_NOTE,
    classify,
    get_meeting_notes,
    split_statements,
)


def test_c004_has_no_notes_and_says_so(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C004")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["no_meeting_notes"]
    assert result.data["note_count"] == 0


def test_c003_note_n006_present_newest_first(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C003")
    assert result.status == OK
    assert [n["note_id"] for n in result.data["notes"]] == ["N-006", "N-007"]
    header = next(f for f in result.facts if f.topic == "note")
    assert header.id == "note:N-006"
    assert header.kind == DATA  # date, author and title are recorded, not claimed
    assert header.text == (
        'Note N-006: "Relationship lunch" on 2026-09-18, written by Tomas Ferreira.'
    )
    assert "up massively" in result.data["notes"][0]["body"]


def test_c003_claims_are_quoted_verbatim_and_stay_reported(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C003")
    renewal = next(f for f in result.facts if f.topic == "renewal")
    assert renewal.id == "note:N-006"
    assert renewal.kind == REPORTED
    assert renewal.text == (
        'Note N-006 (2026-09-18) says: "Renewal "basically agreed" at around +10%, '
        'pending their board."'
    )
    growth = next(f for f in result.facts if f.topic == "growth")
    assert 'streaming usage is "up massively"' in growth.text
    # Every quoted statement is a claim; only the day count is computed and only the
    # two note headers are recorded data.
    assert [f.kind for f in result.facts].count(CALC) == 1
    assert [f.topic for f in result.facts if f.kind == DATA] == ["note", "note"]
    assert all(f.kind == REPORTED for f in result.facts if f.topic not in ("note", "last_meeting"))
    assert all(f.text.startswith("Note N-00") and " says: " in f.text
               for f in result.facts if f.kind == REPORTED)


def test_days_since_last_meeting(ds: Dataset) -> None:
    c003 = get_meeting_notes(ds, "C003")
    assert c003.data["days_since_last_meeting"] == 44
    assert c003.facts[0].kind == CALC
    assert c003.facts[0].text == (
        "2 meeting notes on record; the last meeting was 2026-09-18, 44 days before 2026-11-01."
    )
    c010 = get_meeting_notes(ds, "C010")
    assert c010.data["days_since_last_meeting"] == 263
    assert c010.facts[0].rows == ["note:N-014"]


def test_c001_competitor_and_complaints_are_risk(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C001")
    assert [n["note_id"] for n in result.data["notes"]] == ["N-003", "N-002", "N-001"]
    competitor = next(f for f in result.facts if f.topic == "competitor")
    assert competitor.id == "note:N-003"
    assert competitor.signal == "risk"
    assert 'trialling another in-play odds supplier "for two leagues"' in competitor.text
    complaints = [f for f in result.facts if f.topic == "complaint" and f.id == "note:N-002"]
    assert len(complaints) == 4
    assert all(f.signal == "risk" for f in complaints)


def test_quotes_are_exact_substrings_of_the_body_and_capped(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_meeting_notes(ds, client_id)
        for note in result.data.get("notes", []):
            assert len(note["quotes"]) <= MAX_QUOTES_PER_NOTE
            for quote in note["quotes"]:
                assert quote["text"] in note["body"]


def test_split_and_classify_rules() -> None:
    body = "# Title\n\nDate: 2026-01-01\nAuthor: A\n\n- One thing. Second thing.\n\nActions: none."
    assert split_statements(body) == ["One thing.", "Second thing.", "Actions: none."]
    assert classify("Actions: none.") == "other"
    assert classify("Actions: Maya to send proposal.") == "commitment"
    assert classify("League happy with reporting format.") == "positive"
    assert classify("Good quarter overall.") == "other"
    # A risk or commercial topic wins over the positive group, which is checked last.
    assert classify("Happy with service but worried about delays.") == "complaint"
    assert classify("They are worried about overage bills.") == "complaint"


def _quotes(result, note_id: str) -> list[tuple[str, str, str]]:
    prefix = f"Note {note_id} ("
    return [
        (f.topic, f.signal, f.text.split(" says: ", 1)[1])
        for f in result.facts
        if f.kind == REPORTED and f.text.startswith(prefix)
    ]


def test_c001_n003_positive_statement_is_kept_in_written_order(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C001")
    assert _quotes(result, "N-003") == [
        (
            "competitor",
            "risk",
            '"Head of trading mentioned they are trialling another in-play odds supplier '
            '"for two leagues" since the summer."',
        ),
        (
            "pricing",
            "neutral",
            '"Procurement wants pricing for a reduced in-play scope at renewal."',
        ),
        ("complaint", "risk", '"Budget pressure from their finance team."'),
        (
            "positive",
            "opportunity",
            '"Still positive about the live data feed and pre-match odds."',
        ),
        (
            "commitment",
            "neutral",
            '"Actions: Maya to prepare renewal options before notice date."',
        ),
    ]


def test_c003_n007_is_quoted_in_full(ds: Dataset) -> None:
    result = get_meeting_notes(ds, "C003")
    assert _quotes(result, "N-007") == [
        (
            "other",
            "neutral",
            '"Reviewed alert volumes for the season; two cases escalated to the league '
            'disciplinary panel."',
        ),
        ("positive", "opportunity", '"League happy with reporting format."'),
        ("other", "neutral", '"Actions: none."'),
    ]


def test_c010_and_c008_statements_without_keywords_are_kept(ds: Dataset) -> None:
    assert _quotes(get_meeting_notes(ds, "C010"), "N-014") == [
        ("positive", "opportunity", '"Satisfied with service."'),
        (
            "growth",
            "neutral",
            '"Interested in integrity monitoring if regulation changes in their market."',
        ),
        ("other", "neutral", '"Actions: none."'),
    ]
    assert _quotes(get_meeting_notes(ds, "C008"), "N-008") == [
        ("other", "neutral", '"Presented match visualisation widgets for their website and app."'),
        ("growth", "neutral", '"Strong interest."'),
        ("other", "neutral", '"Proposal to be sent; decision expected before year end."'),
        ("commitment", "neutral", '"Actions: Maya to send proposal."'),
    ]


def test_every_statement_of_every_note_is_quoted(ds: Dataset) -> None:
    for client_id in ds.clients:
        result = get_meeting_notes(ds, client_id)
        assert [g.code for g in result.gaps if g.code == "note_truncated"] == []
        for note in result.data.get("notes", []):
            assert [q["text"] for q in note["quotes"]] == split_statements(note["body"])
            assert note["statement_count"] == len(note["quotes"])


def test_note_longer_than_the_cap_is_admitted_as_a_gap(ds: Dataset) -> None:
    assert MAX_QUOTES_PER_NOTE == 12
    note = next(n for n in ds.notes if n["note_id"] == "N-014")
    body = "\n".join(f"- Point number {i}." for i in range(1, 15))
    long_ds = replace(ds, notes=[{**note, "body": body}])
    result = get_meeting_notes(long_ds, "C010")
    quotes = result.data["notes"][0]["quotes"]
    assert [q["text"] for q in quotes] == [f"Point number {i}." for i in range(1, 13)]
    assert result.data["notes"][0]["statement_count"] == 14
    assert [(g.code, g.text, g.rows) for g in result.gaps] == [
        (
            "note_truncated",
            "Note N-014 has 14 statements; only the first 12 are quoted, the remaining 2 "
            "are not.",
            ["note:N-014"],
        )
    ]

from client_intel.db import Dataset
from client_intel.evidence import CALC, NO_DATA, OK, REPORTED
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
    assert header.kind == REPORTED
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
    # Everything taken from a note is a claim; only the day count is computed.
    assert [f.kind for f in result.facts].count(CALC) == 1
    assert all(f.kind == REPORTED for f in result.facts if f.id.startswith("note:"))


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
    assert classify("Actions: none.") is None
    assert classify("Actions: Maya to send proposal.") == "commitment"
    assert classify("League happy with reporting format.") is None
    assert classify("They are worried about overage bills.") == "complaint"

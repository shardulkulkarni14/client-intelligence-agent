from datetime import date

import pytest

from client_intel.db import Dataset
from client_intel.evidence import NO_DATA, OK, PARTIAL
from client_intel.tools.clients import get_client_profile, resolve_client


@pytest.mark.parametrize(
    ("query", "client_id", "match_type"),
    [
        ("C001", "C001", "id"),
        ("c003", "C003", "id"),
        (" C007 ", "C007", "id"),
        ("Halden Bet", "C001", "exact"),
        ("halden bet", "C001", "case_insensitive"),
        ("Velmont Casino and Sport", "C016", "case_insensitive"),
        ("Brenmoor League", "C003", "words"),
        ("Varrow Racing", "C007", "words"),
        ("Oakhurst Cricket Board", "C011", "exact"),
        ("Halden Bet plc", "C001", "name_in_query"),
        ("Marrow", "C005", "substring"),
        ("Client C001", "C001", "id_in_query"),
        ("client c001 please", "C001", "id_in_query"),
        ("Briefing for C017, thanks", "C017", "id_in_query"),
        ("Athletics", "C014", "words"),
        ("Wexley Athletic", "C017", "words"),
    ],
)
def test_resolves_one_client(ds: Dataset, query: str, client_id: str, match_type: str) -> None:
    result = resolve_client(ds, query)
    assert result.status == OK
    assert result.data["status"] == "resolved"
    assert result.data["client_id"] == client_id
    assert result.data["match_type"] == match_type
    assert [c["client_id"] for c in result.data["candidates"]] == [client_id]
    assert len(result.facts) == 1
    assert result.facts[0].id == f"client:{client_id}"
    assert result.facts[0].rows == [f"client:{client_id}"]
    assert ds.clients[client_id]["client_name"] in result.facts[0].text
    assert result.gaps == []


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Bet", ["C001", "C024"]),
        ("media", ["C002", "C013"]),
        ("League", ["C003", "C018"]),
        ("Fantasy", ["C006", "C019"]),
        # Whole word of "Wexley Athletic FC", start of a word in "Thornbury Athletics
        # Federation".
        ("Athletic", ["C014", "C017"]),
        ("athletic", ["C014", "C017"]),
        ("Athlet", ["C014", "C017"]),
        # Two valid IDs, or an ID next to another client's full name: not guessed.
        ("C001 and C002", ["C001", "C002"]),
        ("Halden Bet (C003)", ["C003", "C001"]),
    ],
)
def test_ambiguous_name_is_not_guessed(ds: Dataset, query: str, expected: list[str]) -> None:
    result = resolve_client(ds, query)
    assert result.status == PARTIAL
    assert result.data["status"] == "ambiguous"
    assert result.data["client_id"] is None
    assert [c["client_id"] for c in result.data["candidates"]] == expected
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["ambiguous_client"]
    assert result.gaps[0].rows == [f"client:{c}" for c in expected]


def test_ambiguous_candidates_carry_names(ds: Dataset) -> None:
    result = resolve_client(ds, "Bet")
    assert result.data["candidates"] == [
        {"client_id": "C001", "client_name": "Halden Bet"},
        {"client_id": "C024", "client_name": "Novaterra Bet"},
    ]


@pytest.mark.parametrize(
    "query", ["Nonexistent Sports Ltd", "C999", "", "   ", "&", "Client C999", "abc001"]
)
def test_unknown_client_is_not_found(ds: Dataset, query: str) -> None:
    result = resolve_client(ds, query)
    assert result.status == NO_DATA
    assert result.data["status"] == "not_found"
    assert result.data["client_id"] is None
    assert result.data["candidates"] == []
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["client_not_found"]


def test_every_client_resolves_by_its_own_name_and_id(ds: Dataset) -> None:
    for client_id, client in ds.clients.items():
        assert resolve_client(ds, client["client_name"]).data["client_id"] == client_id
        assert resolve_client(ds, client["client_name"].upper()).data["client_id"] == client_id
        assert resolve_client(ds, client_id.lower()).data["client_id"] == client_id


def test_profile_c001(ds: Dataset) -> None:
    result = get_client_profile(ds, "C001")
    assert result.status == OK
    assert result.data == {
        "client_id": "C001",
        "client_name": "Halden Bet",
        "segment": "Sportsbook",
        "country": "GB",
        "account_owner": "Maya Lindgren",
        "tier": "Strategic",
        "customer_since": date(2021, 2, 1),
        "missing_fields": [],
    }
    assert len(result.facts) == 1
    fact = result.facts[0]
    assert fact.id == "client:C001"
    for part in ["Halden Bet", "Sportsbook", "GB", "Maya Lindgren", "Strategic", "2021-02-01"]:
        assert part in fact.text


def test_profile_unknown_client(ds: Dataset) -> None:
    result = get_client_profile(ds, "C999")
    assert result.status == NO_DATA
    assert result.facts == []
    assert [g.code for g in result.gaps] == ["client_not_found"]


def test_athletic_names_both_candidates(ds: Dataset) -> None:
    result = resolve_client(ds, "Athletic")
    assert result.data["match_type"] == "substring"
    assert result.data["candidates"] == [
        {"client_id": "C014", "client_name": "Thornbury Athletics Federation"},
        {"client_id": "C017", "client_name": "Wexley Athletic FC"},
    ]
    assert result.gaps[0].text == (
        '"Athletic" matches several clients and none was chosen: '
        "Thornbury Athletics Federation (C014), Wexley Athletic FC (C017)."
    )


def test_a_one_letter_fragment_is_not_a_client(ds):
    from client_intel.tools.clients import resolve_client

    assert resolve_client(ds, "../../x").data["status"] == "not_found"
    assert resolve_client(ds, "x").data["status"] == "not_found"

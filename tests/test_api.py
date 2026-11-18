"""The HTTP API. Nothing here calls a model or the network: the writer is a fake."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from client_intel import api, cli
from client_intel.llm import DEFAULT_MODEL, ModelError

RUN_KEYS = {"ok", "error", "client_id", "client_name", "trigger", "briefing", "evidence",
            "flagged", "repaired"}
INVENTED = "## Bottom line\nUsage fell by 61.7% this year. [contracts:K-0002]"


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path / "runs"


@pytest.fixture
def client(out_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # Run files go to a temporary folder, never to the project's runs/.
    monkeypatch.setenv(api.OUT_ENV, str(out_dir))
    monkeypatch.delenv("CLIENT_INTEL_MODEL", raising=False)
    monkeypatch.delenv(api.DB_ENV, raising=False)

    def no_writer() -> None:
        raise AssertionError("a test reached the real writer")

    # Safe default: a test that forgets to pass a fake fails instead of paying.
    api.app.dependency_overrides[api.get_writer_factory] = lambda: no_writer
    with TestClient(api.app) as test_client:
        yield test_client
    api.app.dependency_overrides.clear()


def use_writer(factory: api.WriterFactory) -> None:
    api.app.dependency_overrides[api.get_writer_factory] = lambda: factory


def assert_error_shape(payload: dict) -> None:
    assert set(payload) == RUN_KEYS
    assert payload["ok"] is False
    assert isinstance(payload["error"], str) and payload["error"]
    assert all(payload[k] is None for k in RUN_KEYS - {"ok", "error"})


def test_health_reports_the_model_and_only_whether_a_key_is_set(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "as_of": "2026-11-01", "model": DEFAULT_MODEL,
                               "model_key_present": True}
    assert "not-a-real-key" not in response.text

    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert client.get("/api/health").json()["model_key_present"] is False


def test_meta_is_the_listing_of_the_command(client, capsys):
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"as_of", "clients", "triggers"}
    assert len(payload["clients"]) == 25
    assert [t["name"] for t in payload["triggers"]] == ["renewal", "meeting_prep", "upsell",
                                                        "at_risk"]
    assert cli.main(["--list"]) == 0
    assert payload == json.loads(capsys.readouterr().out)


def test_offline_briefing_is_ok_with_a_trace_and_leaves_the_run_files(client, out_dir):
    response = client.post("/api/briefings", json={"client": "C001", "trigger": "renewal",
                                                   "use_model": False})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == RUN_KEYS
    assert (payload["ok"], payload["error"]) == (True, None)
    assert (payload["client_id"], payload["client_name"], payload["trigger"]) == (
        "C001", "Halden Bet", "renewal")
    assert (payload["flagged"], payload["repaired"]) == (0, False)
    assert payload["evidence"]["writer"]["mode"] == "offline"
    assert set(payload["evidence"]["trace"]) == {"model", "total_seconds", "total_cost_usd",
                                                 "steps"}
    assert payload["evidence"]["trace"]["steps"][0]["name"] == "plan"
    folder = out_dir / "C001_renewal"
    assert (folder / "briefing.md").read_text() == payload["briefing"]
    assert json.loads((folder / "evidence.json").read_text()) == payload["evidence"]


def test_an_invented_number_is_returned_flagged_with_status_200(client):
    use_writer(lambda: lambda system, user: INVENTED)
    response = client.post("/api/briefings", json={"client": "C001", "trigger": "at_risk"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["flagged"] >= 1
    assert "61.7%" in payload["briefing"]
    assert "UNVERIFIED" in payload["briefing"]
    assert payload["evidence"]["writer"]["mode"] == "model"


def test_ambiguous_client_is_422_and_names_both_candidates(client, out_dir):
    response = client.post("/api/briefings", json={"client": "Bet", "trigger": "renewal",
                                                   "use_model": False})
    assert response.status_code == 422
    payload = response.json()
    assert_error_shape(payload)
    assert "Halden Bet (C001)" in payload["error"]
    assert "Novaterra Bet (C024)" in payload["error"]
    assert not out_dir.exists()


def test_unknown_trigger_is_422(client):
    response = client.post("/api/briefings", json={"client": "C001", "trigger": "birthday",
                                                   "use_model": False})
    assert response.status_code == 422
    payload = response.json()
    assert_error_shape(payload)
    assert "Unknown trigger 'birthday'" in payload["error"]


def test_too_long_context_is_422_with_the_error_shape(client):
    response = client.post("/api/briefings", json={
        "client": "C001", "trigger": "renewal", "context": "x" * 501, "use_model": False})
    assert response.status_code == 422
    payload = response.json()
    assert_error_shape(payload)
    assert payload["error"].startswith("Invalid request: context:")
    assert "500 characters" in payload["error"]


def test_empty_client_and_missing_trigger_are_422_with_the_error_shape(client):
    response = client.post("/api/briefings", json={"client": "   "})
    assert response.status_code == 422
    payload = response.json()
    assert_error_shape(payload)
    assert "client:" in payload["error"] and "trigger:" in payload["error"]


def test_model_error_from_the_writer_factory_is_502(client, out_dir):
    def no_key() -> None:
        raise ModelError("ANTHROPIC_API_KEY is not set.")

    use_writer(no_key)
    response = client.post("/api/briefings", json={"client": "C001", "trigger": "renewal"})
    assert response.status_code == 502
    payload = response.json()
    assert_error_shape(payload)
    assert payload["error"] == "ANTHROPIC_API_KEY is not set."
    assert not out_dir.exists()


def test_use_model_false_never_asks_for_a_writer(client):
    def boom() -> None:
        raise ModelError("must not be called")

    use_writer(boom)
    response = client.post("/api/briefings", json={"client": "C001", "trigger": "renewal",
                                                   "use_model": False})
    assert response.status_code == 200


def test_portfolio_has_every_client_sorted_by_risk_score(client):
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"as_of", "clients"}
    assert payload["as_of"] == "2026-11-01"
    scores = [c["renewal_risk"]["score"] for c in payload["clients"]]
    assert len(scores) == 25
    assert scores == sorted(scores, reverse=True)


def test_the_api_and_the_command_return_the_same_object(client, tmp_path, capsys):
    request = {"client": "C005", "trigger": "meeting_prep", "context": "Call on Friday"}
    from_api = client.post("/api/briefings", json={**request, "use_model": False}).json()
    code = cli.main(["--client", request["client"], "--trigger", request["trigger"],
                     "--context", request["context"], "--no-llm", "--json",
                     "--out", str(tmp_path / "cli")])
    from_cli = json.loads(capsys.readouterr().out)
    assert code == 0
    assert set(from_api) == set(from_cli) == RUN_KEYS
    assert from_api["briefing"] == from_cli["briefing"]
    assert set(from_api["evidence"]) == set(from_cli["evidence"])
    # Everything but the timings is identical between the two callers.
    assert ({k: v for k, v in from_api["evidence"].items() if k != "trace"}
            == {k: v for k, v in from_cli["evidence"].items() if k != "trace"})

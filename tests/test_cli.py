"""The command's machine-readable modes. Nothing here calls a model."""

import json

from client_intel import cli

RUN_KEYS = {"ok", "error", "client_id", "client_name", "trigger", "briefing", "evidence",
            "flagged", "repaired"}


def test_json_mode_prints_exactly_one_object_and_still_writes_files(tmp_path, capsys):
    code = cli.main(["--client", "C001", "--trigger", "renewal", "--no-llm", "--json",
                     "--out", str(tmp_path)])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert set(payload) == RUN_KEYS
    assert (payload["ok"], payload["error"]) == (True, None)
    assert (payload["client_id"], payload["client_name"], payload["trigger"]) == (
        "C001", "Halden Bet", "renewal")
    assert (payload["flagged"], payload["repaired"]) == (0, False)
    assert payload["briefing"].startswith("# Client briefing: Halden Bet (C001), renewal")
    assert set(payload["evidence"]["trace"]) == {"model", "total_seconds", "total_cost_usd",
                                                 "steps"}
    folder = tmp_path / "C001_renewal"
    assert (folder / "briefing.md").read_text() == payload["briefing"]
    assert json.loads((folder / "evidence.json").read_text()) == payload["evidence"]


def test_json_mode_reports_a_request_error_as_an_object(tmp_path, capsys):
    code = cli.main(["--client", "Nobody Ltd", "--trigger", "renewal", "--no-llm", "--json",
                     "--out", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 2
    assert set(payload) == RUN_KEYS
    assert payload["ok"] is False and "Nobody Ltd" in payload["error"]
    assert all(payload[k] is None for k in RUN_KEYS - {"ok", "error"})
    assert "error:" in captured.err
    assert not list(tmp_path.iterdir())


def test_text_mode_is_unchanged(tmp_path, capsys):
    code = cli.main(["--client", "C001", "--trigger", "renewal", "--no-llm",
                     "--out", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == (tmp_path / "C001_renewal" / "briefing.md").read_text() + "\n"
    assert "--- verification:" in captured.err


def test_list_prints_clients_and_triggers(ds, capsys):
    assert cli.main(["--list"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {"as_of", "clients", "triggers"}
    assert payload["as_of"] == "2026-11-01"
    assert [c["client_id"] for c in payload["clients"]] == sorted(ds.clients)
    assert payload["clients"][0] == {
        "client_id": "C001", "client_name": "Halden Bet", "segment": "Sportsbook",
        "tier": "Strategic", "account_owner": "Maya Lindgren"}
    assert [t["name"] for t in payload["triggers"]] == ["renewal", "meeting_prep", "upsell",
                                                        "at_risk"]
    renewal = payload["triggers"][0]
    assert set(renewal) == {"name", "question", "sections"}
    assert renewal["sections"][0] == "Bottom line"


def test_portfolio_prints_the_ranking_and_writes_files_only_with_out(tmp_path, capsys,
                                                                    monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cli.main(["--portfolio"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert set(printed) == {"as_of", "clients"}
    assert len(printed["clients"]) == 25
    assert not list(tmp_path.iterdir())

    out = tmp_path / "ranked"
    assert cli.main(["--portfolio", "--out", str(out)]) == 0
    again = json.loads(capsys.readouterr().out)
    assert again == printed
    assert json.loads((out / "portfolio.json").read_text()) == printed
    table = (out / "portfolio.md").read_text()
    assert "| Rank | Client | Annual value | Contract end | Risk score |" in table
    assert "| 1 | Halden Bet (C001) | EUR 752,000 | 2027-01-31 | 70 |" in table


def test_missing_client_or_trigger_is_a_usage_error(capsys):
    assert cli.main(["--no-llm"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--client and --trigger are required" in captured.err

    assert cli.main(["--client", "C001", "--json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False and payload["client_id"] is None


def test_missing_database_is_exit_code_2(tmp_path, capsys):
    assert cli.main(["--list", "--db", str(tmp_path / "none.db")]) == 2
    assert "Database not found" in capsys.readouterr().err

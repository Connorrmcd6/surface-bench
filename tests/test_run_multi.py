"""Integration test for the runner's --mode multi wiring (offline, mock model, no spend)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from surface_bench import run

_AGENT_FIELDS = {"turns", "stop_reason", "tool_calls", "verified_hidden", "per_turn_tokens"}


def _run(monkeypatch, tmp_path: Path, mode: str) -> tuple[dict, list[dict]]:
    argv = [
        "run", "--models", "mock", "--mode", mode,
        "--scenarios", "cascade-quota-batcher-code", "--trials", "1",
        "--out", str(tmp_path),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    run.main()
    meta = json.loads((tmp_path / "run.json").read_text())
    rows = [json.loads(line) for line in (tmp_path / "raw.jsonl").read_text().splitlines()]
    return meta, rows


def test_multi_mode_writes_agent_fields(monkeypatch, tmp_path: Path) -> None:
    meta, rows = _run(monkeypatch, tmp_path, "multi")
    assert meta["mode"] == "multi" and meta["max_turns"] == 8
    assert rows, "expected rows"
    for r in rows:
        assert r["mode"] == "multi"
        assert _AGENT_FIELDS <= r.keys()
        assert r["stop_reason"] in {"final_answer", "text_answer", "forced_answer"}
        assert isinstance(r["verified_hidden"], bool)


def test_single_mode_omits_agent_fields(monkeypatch, tmp_path: Path) -> None:
    meta, rows = _run(monkeypatch, tmp_path, "single")
    assert meta["mode"] == "single" and meta["max_turns"] is None
    assert rows
    for r in rows:
        assert r["mode"] == "single"
        assert not (_AGENT_FIELDS & r.keys())

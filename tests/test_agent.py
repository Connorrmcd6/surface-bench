"""Offline tests for the multi-turn agent loop (no API, no spend)."""

from __future__ import annotations

from pathlib import Path

import pytest

from surface_bench.agent import run_agent
from surface_bench.models import Step, ToolCall, MockToolModel
from surface_bench.scenarios import load_scenario
from surface_bench.tools_runtime import ToolContext, scenario_sandbox

BENCH_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str, tid: str = "t") -> Step:
    return Step(tool_calls=[ToolCall(id=tid, name="read_file", args={"path": path})], output_tokens=4)


def _final(answer: str, tid: str = "f") -> Step:
    return Step(
        tool_calls=[ToolCall(id=tid, name="final_answer", args={"answer": answer})], output_tokens=6
    )


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    code = tmp_path / "code"
    (code / "limiter").mkdir(parents=True)
    (code / "throttle.py").write_text("def plan_batches(total):\n    return total\n")
    (code / "limiter" / "window.py").write_text("WINDOW_LIMIT = 10  # admits 11 (<=)\n")
    return tmp_path


def test_read_then_final(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    model = MockToolModel(script=[_read("code/limiter/window.py"), _final("VERDICT: capacity=11")])
    traj = run_agent(model, "sys", "task", ctx, max_turns=8)

    assert traj.stop_reason == "final_answer"
    assert traj.final_text == "VERDICT: capacity=11"
    assert traj.turns == 2
    assert ctx.accessed == ["code/limiter/window.py"]
    assert ctx.verified(["code/limiter/*.py"]) is True
    assert [c["name"] for c in traj.tool_calls] == ["read_file", "final_answer"]
    assert traj.output_tokens == 10  # 4 + 6


def test_text_only_answer_terminates(workspace: Path) -> None:
    model = MockToolModel(script=[Step(text="VERDICT: capacity=10", output_tokens=5)])
    traj = run_agent(model, "sys", "task", ToolContext(workspace), max_turns=8)
    assert traj.stop_reason == "text_answer"
    assert traj.final_text == "VERDICT: capacity=10"
    assert traj.turns == 1


def test_bad_call_is_recoverable(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    model = MockToolModel(
        script=[_read("code/missing.py", "1"), _read("code/limiter/window.py", "2"), _final("ok", "3")]
    )
    traj = run_agent(model, "sys", "task", ctx, max_turns=8)
    assert traj.stop_reason == "final_answer"
    assert traj.final_text == "ok"
    assert traj.turns == 3
    # The bad read didn't count as access; the good one did.
    assert ctx.accessed == ["code/limiter/window.py"]


def test_max_turns_forces_an_answer(workspace: Path) -> None:
    # A model that never stops calling tools. With max_turns=2 and an exhausted script, the loop
    # falls back to a forced answer-now turn (MockToolModel returns its text fallback).
    ctx = ToolContext(workspace)
    model = MockToolModel(
        script=[_read("code/throttle.py", "1"), _read("code/throttle.py", "2")],
        fallback="VERDICT: forced",
    )
    traj = run_agent(model, "sys", "task", ctx, max_turns=2)
    assert traj.stop_reason == "forced_answer"
    assert traj.final_text == "VERDICT: forced"
    assert traj.turns == 3  # 2 capped turns + 1 forced


def test_loop_against_real_scenario_sandbox() -> None:
    """End-to-end on a real cascade scenario: the agent reads the hidden dependency it would only
    otherwise know by doc, and that read registers as verification."""
    scenario = load_scenario(BENCH_ROOT / "scenarios" / "cascade-quota-batcher-code")
    with scenario_sandbox(scenario) as ws:
        ctx = ToolContext(ws)
        model = MockToolModel(
            script=[_read("code/limiter/window.py"), _final("FILE: code/throttle.py\n```python\nx=1\n```")]
        )
        traj = run_agent(model, "sys", "task", ctx, max_turns=8)
        assert traj.stop_reason == "final_answer"
        assert ctx.verified(scenario.hidden_paths) is True
        assert any(c["name"] == "read_file" for c in traj.tool_calls)

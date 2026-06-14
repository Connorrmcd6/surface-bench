"""Offline tests for the read-only agent tool surface and per-trial sandbox (no API, no spend)."""

from __future__ import annotations

from pathlib import Path

import pytest

from surface_bench.prompts import build_prompt
from surface_bench.scenarios import load_scenario
from surface_bench.tools_runtime import (
    TOOL_NAMES,
    TOOL_SPECS,
    ToolContext,
    dispatch,
    scenario_sandbox,
)

BENCH_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A minimal sandbox: a code/ tree with a visible file and a 'hidden' dependency."""
    code = tmp_path / "code"
    (code / "limiter").mkdir(parents=True)
    (code / "throttle.py").write_text("def plan_batches(total):\n    return total\n")
    (code / "limiter" / "window.py").write_text(
        "WINDOW_LIMIT = 10\n\nclass FixedWindowLimiter:\n    def allow(self, n):\n        return n <= self.limit\n"
    )
    return tmp_path


def test_list_dir(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    assert ctx.list_dir(".") == "code/"
    assert set(ctx.list_dir("code").split("\n")) == {"limiter/", "throttle.py"}


def test_read_file_and_access_tracking(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    assert ctx.accessed == []
    body = ctx.read_file("code/limiter/window.py")
    assert "WINDOW_LIMIT = 10" in body
    assert ctx.accessed == ["code/limiter/window.py"]


def test_grep(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    out = ctx.grep("WINDOW_LIMIT", "code")
    assert "code/limiter/window.py:1: WINDOW_LIMIT = 10" in out
    assert "code/limiter/window.py" in ctx.accessed
    assert ctx.grep("nomatchhere", "code") == "(no matches)"


def test_grep_invalid_regex_is_recoverable(workspace: Path) -> None:
    out, is_final = dispatch("grep", {"pattern": "("}, ToolContext(workspace))
    assert out.startswith("error: invalid regex")
    assert is_final is False


@pytest.mark.parametrize("bad", ["../etc/passwd", "/etc/passwd", "code/../../secret"])
def test_path_escape_rejected(workspace: Path, bad: str) -> None:
    out, is_final = dispatch("read_file", {"path": bad}, ToolContext(workspace))
    assert out.startswith("error:") and "escapes the workspace" in out
    assert is_final is False


def test_missing_file_is_recoverable(workspace: Path) -> None:
    out, _ = dispatch("read_file", {"path": "code/nope.py"}, ToolContext(workspace))
    assert out.startswith("error: no such file")


def test_final_answer_terminates(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    out, is_final = dispatch("final_answer", {"answer": "VERDICT: x=1"}, ctx)
    assert is_final is True
    assert ctx.final_answer == "VERDICT: x=1"


def test_unknown_tool_and_missing_arg(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    out, is_final = dispatch("delete_everything", {}, ctx)
    assert out == "error: unknown tool 'delete_everything'" and is_final is False
    out, _ = dispatch("read_file", {}, ctx)  # missing required 'path'
    assert out.startswith("error: missing required argument")


def test_verified_helper(workspace: Path) -> None:
    ctx = ToolContext(workspace)
    hidden = ["code/limiter/*.py"]
    assert ctx.verified(hidden) is False
    ctx.read_file("code/throttle.py")  # visible file — not verification
    assert ctx.verified(hidden) is False
    ctx.read_file("code/limiter/window.py")  # the hidden dependency
    assert ctx.verified(hidden) is True


def test_tool_specs_contract() -> None:
    # The neutral schema each provider adapter will translate. Guard its shape so an adapter can
    # rely on every spec having a name + a JSON-Schema `parameters` object.
    assert {"list_dir", "read_file", "grep", "final_answer"} == set(TOOL_NAMES)
    for spec in TOOL_SPECS:
        assert spec.keys() >= {"name", "description", "parameters"}
        assert spec["parameters"]["type"] == "object"
        assert "properties" in spec["parameters"]


def test_sandbox_exposes_hidden_dependency_that_prompt_hides() -> None:
    """The keystone of the multi-turn design: a real cascade scenario's hidden dependency is absent
    from the prompt but reachable via tools in the sandbox."""
    scenario = load_scenario(BENCH_ROOT / "scenarios" / "cascade-quota-batcher-code")
    assert scenario.hidden_paths, "expected a cascade scenario with hidden_paths"

    _, user = build_prompt(scenario, "C1")
    assert "### code/limiter/window.py" not in user  # the dependency is withheld from the prompt

    with scenario_sandbox(scenario) as ws:
        ctx = ToolContext(ws)
        assert (ws / "code" / "limiter" / "window.py").is_file()  # but present on disk
        body = ctx.read_file("code/limiter/window.py")  # and reachable by choice
        assert body.strip() != ""
        assert ctx.verified(scenario.hidden_paths) is True

"""Offline tests for the Anthropic tool-use translation (no network — pure converters + a fake
response). The live round-trip is covered by a manual smoke, not the suite."""

from __future__ import annotations

from types import SimpleNamespace

from surface_bench.models import (
    Step,
    ToolCall,
    _anthropic_messages,
    _anthropic_tools,
    _step_from_anthropic,
)
from surface_bench.tools_runtime import TOOL_SPECS


def test_tools_translate_to_input_schema() -> None:
    out = _anthropic_tools(TOOL_SPECS)
    assert {t["name"] for t in out} == {"list_dir", "read_file", "grep", "final_answer"}
    for spec, t in zip(TOOL_SPECS, out):
        assert t["input_schema"] == spec["parameters"]  # Anthropic's field name
        assert set(t) == {"name", "description", "input_schema"}


def test_messages_roundtrip_and_coalescing() -> None:
    # Assistant turn produced by the adapter carries provider_msg (echoed verbatim).
    asst = Step(
        tool_calls=[ToolCall(id="t1", name="read_file", args={"path": "code/x.py"})],
        provider_msg=[{"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "code/x.py"}}],
    )
    messages = [
        {"role": "user", "content": "do the task"},
        {"role": "assistant", "step": asst},
        {"role": "tool", "results": [{"id": "t1", "content": "WINDOW_LIMIT = 10"}]},
        {"role": "user", "content": "answer now"},  # the forced-answer nudge
    ]
    out = _anthropic_messages(messages)

    # roles must alternate: user, assistant, user  (the tool-result turn + nudge are coalesced)
    assert [m["role"] for m in out] == ["user", "assistant", "user"]
    assert out[1]["content"] == asst.provider_msg
    last = out[2]["content"]
    assert last[0]["type"] == "tool_result" and last[0]["tool_use_id"] == "t1"
    assert last[1] == {"type": "text", "text": "answer now"}


def test_messages_reconstruct_when_no_provider_msg() -> None:
    # A Step without provider_msg (e.g. a mock) is reconstructed into valid blocks.
    asst = Step(text="thinking", tool_calls=[ToolCall(id="t1", name="grep", args={"pattern": "x"})])
    out = _anthropic_messages([{"role": "assistant", "step": asst}])
    blocks = out[0]["content"]
    assert {"type": "text", "text": "thinking"} in blocks
    assert {"type": "tool_use", "id": "t1", "name": "grep", "input": {"pattern": "x"}} in blocks


def test_step_parsed_from_response() -> None:
    resp = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", text="let me check"),
            SimpleNamespace(type="tool_use", id="t9", name="read_file", input={"path": "code/x.py"}),
        ],
        usage=SimpleNamespace(input_tokens=120, output_tokens=18),
        stop_reason="tool_use",
    )
    step = _step_from_anthropic(resp)
    assert step.text == "let me check"
    assert step.tool_calls == [ToolCall(id="t9", name="read_file", args={"path": "code/x.py"})]
    assert (step.input_tokens, step.output_tokens) == (120, 18)
    assert step.stop_reason == "tool_use"
    # provider_msg must round-trip back into a valid assistant message
    assert _anthropic_messages([{"role": "assistant", "step": step}])[0]["content"] == step.provider_msg

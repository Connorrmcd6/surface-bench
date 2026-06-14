"""Provider-agnostic model adapters.

Every model implements `complete(system, user) -> Completion`. Anthropic is the first provider;
adding OpenAI/Gemini/etc. means writing one more class behind the same protocol and registering it
in `build_model`. Nothing else in the harness knows which provider produced a completion.

`Completion` carries token usage. We compare *output* tokens across conditions: input tokens differ
by construction (the doc block's size), so they are structural, not a behavioural signal; output
tokens are where the cost of reconciling a stale doc against the code actually shows up.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw_usage: dict = field(default_factory=dict)


class Model(Protocol):
    name: str

    def complete(self, system: str, user: str) -> Completion: ...


# ---- Multi-turn (agentic) types ------------------------------------------------------------
# A provider-neutral one-turn result. Each adapter (Anthropic/OpenAI/Gemini) translates its wire
# response into a `Step` and stashes the raw assistant message in `provider_msg`, so the agent loop
# can echo it back verbatim on the next turn without the loop ever learning the provider's shape.


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict


@dataclass
class Step:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""
    provider_msg: Any = None  # raw assistant message, re-sent verbatim into history


class ToolModel(Protocol):
    """A model that can run the multi-turn loop. Separate from `Model` so single-shot-only adapters
    don't have to implement `step`. `messages` is the neutral history built by `agent.run_agent`."""

    name: str

    def step(self, system: str, messages: list[dict], tools: list[dict]) -> Step: ...


class MockModel:
    """Offline model for pipeline tests. Returns a canned reply (optionally per-condition).

    `replies` maps a condition label -> reply text; `default` is used otherwise. This lets a
    dry run exercise grading, metrics, and reporting with no network or API key.
    """

    def __init__(self, name: str = "mock", default: str = "", replies: dict | None = None):
        self.name = name
        self._default = default
        self._replies = replies or {}
        self._condition: str | None = None

    def set_condition(self, condition: str) -> None:
        self._condition = condition

    def complete(self, system: str, user: str) -> Completion:
        text = self._replies.get(self._condition, self._default)
        # Synthetic output-token count so metrics/report have something to aggregate offline.
        return Completion(text=text, input_tokens=len(user.split()), output_tokens=len(text.split()))


class MockToolModel:
    """Offline tool-using model for loop tests: returns a fixed `script` of `Step`s, one per call.

    Once the script is exhausted it falls back to a text-only `Step` (no tool calls), which the loop
    treats as a final answer — so a script that never calls `final_answer` still terminates cleanly
    (exercising the max-turns / forced-answer path). No network, no key.
    """

    def __init__(
        self,
        name: str = "mock-tool",
        script: list[Step] | None = None,
        fallback: str = "",
        default: str = "",
        replies: dict | None = None,
    ):
        self.name = name
        self._script = list(script or [])
        self._fallback = fallback
        self._default = default
        self._replies = replies or {}
        self._condition: str | None = None
        self._i = 0

    def set_condition(self, condition: str) -> None:
        self._condition = condition

    def step(self, system: str, messages: list[dict], tools: list[dict]) -> Step:
        if self._i < len(self._script):
            step = self._script[self._i]
            self._i += 1
            return step
        if self._fallback:
            # Text-only turn -> the loop accepts it as the answer (exercises the forced-answer path).
            return Step(text=self._fallback, output_tokens=len(self._fallback.split()))
        # Canned mode (run.py offline smoke): answer immediately with the condition's reply.
        reply = self._replies.get(self._condition, self._default)
        return Step(
            tool_calls=[ToolCall(id="final", name="final_answer", args={"answer": reply})],
            output_tokens=len(reply.split()),
        )


# ---- Anthropic tool-use translation ---------------------------------------------------------
# Pure converters between the neutral loop format (agent.run_agent) and the Anthropic wire format,
# kept at module scope so they can be unit-tested without a network call (the riskiest part of any
# provider adapter is the message/tool round-trip).


def _anthropic_tools(tools: list[dict]) -> list[dict]:
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["parameters"]}
        for t in tools
    ]


def _anthropic_blocks_from_step(step: Step) -> list[dict]:
    # Fallback reconstruction when a Step has no provider_msg (e.g. a mock); the real adapter always
    # stores provider_msg, so this just keeps history valid for non-Anthropic-authored turns.
    blocks: list[dict] = []
    if step.text:
        blocks.append({"type": "text", "text": step.text})
    for tc in step.tool_calls:
        blocks.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.args})
    return blocks


def _anthropic_messages(messages: list[dict]) -> list[dict]:
    # Anthropic requires alternating roles, so we coalesce consecutive same-role turns — in
    # particular a tool_result user-turn followed by a nudge user-turn become one user message.
    out: list[dict] = []

    def push(role: str, blocks: list[dict]) -> None:
        if out and out[-1]["role"] == role:
            out[-1]["content"].extend(blocks)
        else:
            out.append({"role": role, "content": list(blocks)})

    for m in messages:
        if m["role"] == "user":
            push("user", [{"type": "text", "text": m["content"]}])
        elif m["role"] == "assistant":
            step = m["step"]
            blocks = step.provider_msg if step.provider_msg is not None else _anthropic_blocks_from_step(step)
            push("assistant", blocks)
        elif m["role"] == "tool":
            push(
                "user",
                [
                    {"type": "tool_result", "tool_use_id": r["id"], "content": r["content"]}
                    for r in m["results"]
                ],
            )
    return out


def _step_from_anthropic(resp) -> Step:
    text = ""
    calls: list[ToolCall] = []
    provider: list[dict] = []
    for b in resp.content:
        btype = getattr(b, "type", None)
        if btype == "text":
            text += b.text
            provider.append({"type": "text", "text": b.text})
        elif btype == "tool_use":
            args = dict(b.input)
            calls.append(ToolCall(id=b.id, name=b.name, args=args))
            provider.append({"type": "tool_use", "id": b.id, "name": b.name, "input": args})
    u = resp.usage
    return Step(
        text=text,
        tool_calls=calls,
        input_tokens=getattr(u, "input_tokens", 0),
        output_tokens=getattr(u, "output_tokens", 0),
        stop_reason=getattr(resp, "stop_reason", "") or "",
        provider_msg=provider,
    )


class AnthropicModel:
    def __init__(self, name: str, model_id: str, temperature: float, max_tokens: int):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise SystemExit("pip install anthropic (see bench/pyproject.toml)") from e
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set")
        self.name = name
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        # Per-request timeout + retries so a single hung request can't stall the whole matrix
        # (the SDK default has no wall-clock cap short enough for a long unattended run).
        self._client = anthropic.Anthropic(timeout=120.0, max_retries=4)

    def complete(self, system: str, user: str) -> Completion:
        resp = self._client.messages.create(
            model=self.model_id,
            system=system,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        u = resp.usage
        return Completion(
            text=text,
            input_tokens=getattr(u, "input_tokens", 0),
            output_tokens=getattr(u, "output_tokens", 0),
            raw_usage=u.model_dump() if hasattr(u, "model_dump") else {},
        )

    def step(self, system: str, messages: list[dict], tools: list[dict]) -> Step:
        resp = self._client.messages.create(
            model=self.model_id,
            system=system,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            tools=_anthropic_tools(tools),
            messages=_anthropic_messages(messages),
        )
        return _step_from_anthropic(resp)


def build_model(
    name: str, spec: dict, *, temperature: float, max_tokens: int, mode: str = "single"
) -> Model:
    provider = spec.get("provider")
    if provider == "mock":
        if mode == "multi":
            return MockToolModel(
                name=name, default=spec.get("default", ""), replies=spec.get("replies")
            )
        return MockModel(name=name, default=spec.get("default", ""), replies=spec.get("replies"))
    if provider == "anthropic":
        return AnthropicModel(
            name=name,
            model_id=spec["model_id"],
            temperature=spec.get("temperature", temperature),
            max_tokens=spec.get("max_tokens", max_tokens),
        )
    raise ValueError(f"unknown provider {provider!r} for model {name!r}")

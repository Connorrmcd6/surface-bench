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
from typing import Protocol


@dataclass
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw_usage: dict = field(default_factory=dict)


class Model(Protocol):
    name: str

    def complete(self, system: str, user: str) -> Completion: ...


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
        self._client = anthropic.Anthropic()

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


def build_model(name: str, spec: dict, *, temperature: float, max_tokens: int) -> Model:
    provider = spec.get("provider")
    if provider == "mock":
        return MockModel(name=name, default=spec.get("default", ""), replies=spec.get("replies"))
    if provider == "anthropic":
        return AnthropicModel(
            name=name,
            model_id=spec["model_id"],
            temperature=spec.get("temperature", temperature),
            max_tokens=spec.get("max_tokens", max_tokens),
        )
    raise ValueError(f"unknown provider {provider!r} for model {name!r}")

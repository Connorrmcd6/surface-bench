"""The multi-turn agent loop (v2 / milestone #12).

Drives a `ToolModel` over the read-only tool surface (`tools_runtime`) until it submits a final
answer or runs out of turns. The loop is provider-agnostic: it only ever sees neutral `Step`/
`ToolCall` objects and a neutral message history; each model adapter owns the translation to/from
its wire format (and stashes the raw assistant message in `Step.provider_msg` so history round-trips
losslessly).

Neutral message schema (what `messages` holds, oldest first) — the contract each adapter reads:

    {"role": "user",      "content": str}                         # the initial task, or a nudge
    {"role": "assistant", "step": Step}                           # one model turn (carries provider_msg)
    {"role": "tool",      "results": [{"id": str, "content": str}]}  # results for the prior turn's calls

Termination, in priority order:
  1. the model calls `final_answer`        -> stop_reason "final_answer"
  2. the model emits text and no tool calls -> stop_reason "text_answer" (trailing text is the answer)
  3. `max_turns` reached mid-tool-use       -> one forced "answer now" nudge -> stop_reason "forced_answer"

The final answer is graded by the *existing* deterministic graders exactly as in single-shot, so the
two modes stay comparable: it must still carry the scenario's `VERDICT:` line or `FILE:` blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Step, ToolModel
from .tools_runtime import TOOL_SPECS, ToolContext, dispatch

NUDGE = (
    "You have reached the step limit. Call final_answer now with your complete answer "
    "(including any required VERDICT line or FILE: blocks)."
)


@dataclass
class Trajectory:
    final_text: str
    turns: int
    stop_reason: str
    tool_calls: list[dict] = field(default_factory=list)  # [{turn, name, args}]
    accessed: list[str] = field(default_factory=list)  # workspace-relative paths read/grepped
    input_tokens: int = 0
    output_tokens: int = 0
    per_turn_tokens: list[tuple[int, int]] = field(default_factory=list)


def run_agent(
    model: ToolModel,
    system: str,
    user: str,
    ctx: ToolContext,
    *,
    tools: list[dict] = TOOL_SPECS,
    max_turns: int = 8,
) -> Trajectory:
    messages: list[dict] = [{"role": "user", "content": user}]
    tool_log: list[dict] = []
    per_turn: list[tuple[int, int]] = []
    in_tok = out_tok = 0
    final: str | None = None
    stop = ""
    turns = 0

    def _account(step: Step) -> None:
        nonlocal in_tok, out_tok
        in_tok += step.input_tokens
        out_tok += step.output_tokens
        per_turn.append((step.input_tokens, step.output_tokens))

    while turns < max_turns:
        turns += 1
        step = model.step(system, messages, tools)
        _account(step)
        messages.append({"role": "assistant", "step": step})

        if not step.tool_calls:
            # Text-only turn: providers vary on whether they reliably call a terminal tool, so we
            # accept trailing prose as the answer.
            final, stop = step.text, "text_answer"
            break

        results = []
        ended = False
        for tc in step.tool_calls:
            tool_log.append({"turn": turns, "name": tc.name, "args": tc.args})
            out, is_final = dispatch(tc.name, tc.args, ctx)
            results.append({"id": tc.id, "content": out})
            ended = ended or is_final
        messages.append({"role": "tool", "results": results})
        if ended:
            final, stop = ctx.final_answer or "", "final_answer"
            break

    if final is None:
        # Exhausted the budget still mid-tool-use: one forced answer-now turn.
        messages.append({"role": "user", "content": NUDGE})
        turns += 1
        step = model.step(system, messages, tools)
        _account(step)
        messages.append({"role": "assistant", "step": step})
        final = ""
        for tc in step.tool_calls:
            tool_log.append({"turn": turns, "name": tc.name, "args": tc.args})
            out, is_final = dispatch(tc.name, tc.args, ctx)
            if is_final:
                final = ctx.final_answer or ""
        if not final:
            final = step.text
        stop = "forced_answer"

    return Trajectory(
        final_text=final,
        turns=turns,
        stop_reason=stop,
        tool_calls=tool_log,
        accessed=list(ctx.accessed),
        input_tokens=in_tok,
        output_tokens=out_tok,
        per_turn_tokens=per_turn,
    )

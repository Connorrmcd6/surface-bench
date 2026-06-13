"""Assemble the (system, user) prompt for a scenario under a given condition.

Only the *documentation block* differs across conditions; the code, task, and system prompt are
byte-identical. That is what makes any C2-vs-C1 gap attributable to doc *accuracy* rather than to
the mere presence of prose (C0 isolates presence).
"""

from __future__ import annotations

from fnmatch import fnmatch

from .scenarios import Scenario

CONDITIONS = ("C0", "C1", "C2", "C3")

CONDITION_LABEL = {
    "C0": "code only (no documentation)",
    "C1": "code + stale documentation",
    "C2": "code + fresh documentation",
    "C3": "code + stale documentation + surf divergence report",
}

SYSTEM = (
    "You are an expert software engineer assisting a teammate. Use the materials provided — the "
    "project documentation and any source code — to answer precisely."
)

_FENCE_LANG = {".py": "python", ".ts": "typescript", ".tsx": "tsx", ".js": "javascript"}


def _render_code(scenario: Scenario) -> str:
    # Cascade scenarios hide the drifted *dependency*: its real source stays in code/ (so surf
    # seals a genuine divergence and the grader runs against it) but is withheld from the prompt,
    # so the agent only knows the dependency through its doc. fnmatch lets meta list a file or a
    # glob (e.g. "code/limiter/*.py").
    hidden = scenario.hidden_paths
    blocks = ["## Codebase\n"]
    for f in scenario.code:
        if any(fnmatch(f.relpath, pat) for pat in hidden):
            continue
        suffix = "." + f.relpath.rsplit(".", 1)[-1] if "." in f.relpath else ""
        lang = _FENCE_LANG.get(suffix, "")
        blocks.append(f"### {f.relpath}\n```{lang}\n{f.content.rstrip()}\n```")
    return "\n\n".join(blocks)


def _doc_block(scenario: Scenario, condition: str) -> str:
    if condition == "C0":
        return ""
    hub = scenario.hub_fresh if condition == "C2" else scenario.hub_stale
    block = f"## Project documentation\n\nThe repository documents this area as follows:\n\n{hub.rstrip()}"
    if condition == "C3":
        block += (
            "\n\n## Automated documentation check\n\n"
            "Surface (a deterministic doc-drift gate) reports that the anchored claim above no "
            "longer matches the code it points at — the documented span has changed since the "
            "claim was last confirmed:\n\n"
            f"```json\n{scenario.surf_report.rstrip()}\n```"
        )
    return block


def build_prompt(scenario: Scenario, condition: str) -> tuple[str, str]:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}")
    parts = [_render_code(scenario)]
    doc = _doc_block(scenario, condition)
    if doc:
        parts.append(doc)
    parts.append(f"## Task\n\n{scenario.task.rstrip()}")
    return SYSTEM, "\n\n".join(parts)

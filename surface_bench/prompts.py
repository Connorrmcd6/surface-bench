"""Assemble the (system, user) prompt for a scenario under a given condition.

Only the *documentation block* differs across conditions; the code, task, and system prompt are
byte-identical. That is what makes any C2-vs-C1 gap attributable to doc *accuracy* rather than to
the mere presence of prose (C0 isolates presence).
"""

from __future__ import annotations

from fnmatch import fnmatch

from .scenarios import Scenario

CONDITIONS = ("C0", "C1", "C2", "C3", "Cw")

CONDITION_LABEL = {
    "C0": "code only (no documentation)",
    "C1": "code + stale documentation",
    "C2": "code + fresh documentation",
    "C3": "code + stale documentation + surf divergence report",
    "Cw": "code + stale documentation + generic staleness warning",
}

# Deliberately minimal and persona-free: no "you are an expert…" framing (which primes diligent,
# skeptical behaviour) and no precedence between docs and code. This mirrors how people actually
# prompt — paste/tag some files, maybe a doc, ask for the change — and keeps the docs-vs-code
# question entirely to the model.
SYSTEM = "Use the files and documentation provided to do the task below."

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
    if condition == "Cw":
        # Control isolating Surface's *specific* contribution: a generic staleness warning with no
        # corrected code, no file, no line, no value. If Cw recovers like C3, the value was just
        # "any skepticism prompt"; if Cw stays at C1, only Surface's concrete fix helps. Keep this
        # deliberately content-free — leaking the truth here would collapse the C3-vs-Cw contrast.
        block += (
            "\n\n## Note\n\n"
            "This documentation may be out of date. It was last reviewed some time ago and might "
            "no longer reflect the current behaviour of the code."
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

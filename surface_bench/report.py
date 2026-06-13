"""Turn a results dir into summary.json, a markdown report, and (optional) plots.

    python -m surface_bench.report results/<timestamp>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .metrics import load_rows, summarize
from .prompts import CONDITION_LABEL

DELTA_GLOSS = {
    "C2-C1": "fresh vs stale (the Surface value)",
    "C0-C1": "no-docs vs stale (rotted worse than nothing?)",
    "C3-C1": "surf-report vs stale (does surfacing drift recover it?)",
    "C2-C0": "fresh vs no-docs (value of accurate prose)",
}

TOKEN_DELTA_GLOSS = {
    "C1-C2": "stale − fresh (extra generation to cope with a stale doc)",
    "C1-C0": "stale − no-docs (does a wrong doc cost more than none?)",
    "C1-C3": "stale − stale+report (does the surf report cut the cost?)",
}


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.0f}%"


def _ci(ci) -> str:
    return "" if not ci else f" [{100 * ci[0]:.0f}–{100 * ci[1]:.0f}]"


def _tok(x: float | None) -> str:
    return "—" if x is None else f"{x:.0f}"


def _ci_raw(ci) -> str:
    return "" if not ci else f" [{ci[0]:.0f}–{ci[1]:.0f}]"


TIER_LABEL = {
    "T0": "local (contradiction visible)",
    "T1": "buried (truth needs tracing)",
    "T2": "premise (invariant is load-bearing)",
    "T3": "multi-claim (one of several drifted)",
}


def _gradient_table(summary: dict) -> list[str]:
    """The headline: does C2-C1 (the Surface effect) grow with complexity tier?"""
    tiers = summary.get("tiers", [])
    if len(tiers) < 2:
        return []
    lines = ["## The gradient — Surface effect (C2−C1 success) by complexity tier\n"]
    for model in summary["models"]:
        lines.append(f"### {model}\n")
        lines.append("| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |")
        lines.append("|---|---|---|")
        for tier in tiers:
            block = summary["by_tier"][tier][model]

            def cell(key):
                d = block.get(key)
                if not d:
                    return "—"
                star = " ✓" if d["significant"] else ""
                return f"{100 * d['delta']:+.0f} pp [{100 * d['ci'][0]:+.0f}, {100 * d['ci'][1]:+.0f}]{star}"

            label = TIER_LABEL.get(tier, "")
            lines.append(f"| {tier} — {label} | {cell('C2-C1')} | {cell('C0-C1')} |")
        lines.append("")
    return lines


def _spend_section(summary: dict) -> list[str]:
    cost = summary.get("cost")
    if not cost or not cost.get("total_usd"):
        return []
    lines = [f"## Spend\n\n**Total: ${cost['total_usd']:.2f}** (estimated from token usage).\n"]
    by_model = {m: v for m, v in cost["by_model"].items() if v}
    if by_model:
        lines.append("| Model | Spend |")
        lines.append("|---|---|")
        for m, v in by_model.items():
            lines.append(f"| {m} | ${v:.2f} |")
        lines.append("")
    return lines


def render_markdown(summary: dict) -> str:
    lines = ["# Surface agent-impact benchmark\n"]
    lines += _spend_section(summary)
    lines += _gradient_table(summary)
    for model in summary["models"]:
        lines.append(f"## {model}\n")
        lines.append("| Condition | n | Success | Misled |")
        lines.append("|---|---|---|---|")
        for cond in summary["conditions"]:
            r = summary["rates"][model][cond]
            label = CONDITION_LABEL.get(cond, cond)
            lines.append(
                f"| {cond} — {label} | {r['n']} | {_pct(r['success'])}{_ci(r['success_ci'])} "
                f"| {_pct(r['misled'])}{_ci(r['misled_ci'])} |"
            )
        lines.append("\n**Deltas (success rate, 95% bootstrap CI):**\n")
        for key, d in summary["deltas"][model].items():
            sig = " ✓ significant" if d["significant"] else ""
            gloss = DELTA_GLOSS.get(key, "")
            lines.append(
                f"- `{key}` {gloss}: {100 * d['delta']:+.0f} pp "
                f"[{100 * d['ci'][0]:+.0f}, {100 * d['ci'][1]:+.0f}]{sig}"
            )

        toks = summary.get("tokens", {}).get(model, {})
        if toks:
            lines.append("\n**Output tokens (mean, 95% bootstrap CI) — generation cost:**\n")
            lines.append("| Condition | mean out | when correct | when misled |")
            lines.append("|---|---|---|---|")
            for cond in summary["conditions"]:
                t = toks.get(cond, {})
                lines.append(
                    f"| {cond} | {_tok(t.get('mean_output'))}{_ci_raw(t.get('mean_output_ci'))} "
                    f"| {_tok(t.get('mean_output_correct'))} | {_tok(t.get('mean_output_misled'))} |"
                )
            lines.append("\n**Output-token deltas (95% bootstrap CI):**\n")
            for key, d in summary.get("token_deltas", {}).get(model, {}).items():
                sig = " ✓ significant" if d["significant"] else ""
                gloss = TOKEN_DELTA_GLOSS.get(key, "")
                lines.append(
                    f"- `{key}` {gloss}: {d['delta']:+.0f} tok "
                    f"[{d['ci'][0]:+.0f}, {d['ci'][1]:+.0f}]{sig}"
                )
        lines.append("")
    return "\n".join(lines)


def maybe_plot(summary: dict, out_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    conds = summary["conditions"]
    for model in summary["models"]:
        succ = [summary["rates"][model][c]["success"] or 0 for c in conds]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(conds, [100 * s for s in succ], color="#3b6")
        ax.set_ylim(0, 100)
        ax.set_ylabel("success rate (%)")
        ax.set_title(f"{model}: success by condition")
        fig.tight_layout()
        fig.savefig(out_dir / f"success_{model}.png", dpi=120)
        plt.close(fig)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python -m surface_bench.report results/<timestamp>")
    out_dir = Path(sys.argv[1])
    rows = load_rows(out_dir)
    summary = summarize(rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    md = render_markdown(summary)
    (out_dir / "report.md").write_text(md + "\n")
    maybe_plot(summary, out_dir)
    print(md)


if __name__ == "__main__":
    main()

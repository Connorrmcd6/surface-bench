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
    "C3-Cw": "surf-report vs bare warning (is the value the *fix*, not just suspicion?)",
    "Cw-C1": "bare warning vs stale (does a generic warning alone help?)",
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


def _verification_section(summary: dict) -> list[str]:
    """The headline of the multi-turn track: a confident stale doc should suppress the file-read the
    agent would otherwise do (H4), and within C1 verifiers should be right, non-verifiers misled (H5)."""
    ver = summary.get("verification")
    if not ver:
        return []
    lines = [
        "## Verification — did the agent check the hidden dependency? (multi-turn)\n",
        "With no doc the agent should go read the hidden code; a confident **stale** doc should "
        "suppress that check (H4). Within C1, those who verified should be correct (H5).\n",
    ]
    for model in summary["models"]:
        lines.append(f"### {model}\n")
        lines.append("| Condition | n | Verified hidden dep | When verified, correct |")
        lines.append("|---|---|---|---|")
        for cond in summary["conditions"]:
            v = ver.get(model, {}).get(cond)
            if not v:
                continue
            lines.append(
                f"| {cond} | {v['n']} | {_pct(v['verification_rate'])}{_ci(v['verification_ci'])} "
                f"| {_pct(v['verified_then_correct'])} |"
            )
        for key, d in summary.get("verification_deltas", {}).get(model, {}).items():
            sig = " ✓ significant" if d["significant"] else ""
            lines.append(
                f"\n- verification `{key}`: {100 * d['delta']:+.0f} pp "
                f"[{100 * d['ci'][0]:+.0f}, {100 * d['ci'][1]:+.0f}]{sig}"
            )
        med = summary.get("mediation", {}).get(model)
        if med and (med["n_verified"] or med["n_unverified"]):
            lines.append(
                f"- C1 mediation (H5): verifiers {_pct(med['verified_success'])} correct "
                f"(n={med['n_verified']}) vs non-verifiers {_pct(med['unverified_success'])} "
                f"(n={med['n_unverified']})"
            )
        lines.append("")
    return lines


def _per_scenario_section(summary: dict) -> list[str]:
    """Per-scenario success, so one broken fixture can't hide inside a family average."""
    bs = summary.get("by_scenario")
    if not bs:
        return []
    conds = summary["conditions"]
    lines = ["## Per-scenario success rate\n"]
    for model in summary["models"]:
        lines.append(f"### {model}\n")
        lines.append("| Scenario | " + " | ".join(conds) + " |")
        lines.append("|" + "---|" * (len(conds) + 1))
        for sc in sorted(bs):
            cells = bs[sc].get(model, {})
            row = [sc] + [_pct(cells[c]["success"]) if c in cells else "—" for c in conds]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return lines


def render_markdown(summary: dict) -> str:
    lines = ["# Surface agent-impact benchmark\n"]
    lines += _spend_section(summary)
    lines += _gradient_table(summary)
    lines += _verification_section(summary)
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
            holm = " (Holm ✓)" if d.get("significant_holm") else (" (Holm ✗)" if "significant_holm" in d else "")
            gloss = DELTA_GLOSS.get(key, "")
            lines.append(
                f"- `{key}` {gloss}: {100 * d['delta']:+.0f} pp "
                f"[{100 * d['ci'][0]:+.0f}, {100 * d['ci'][1]:+.0f}]{sig}{holm}"
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
    lines += _per_scenario_section(summary)
    return "\n".join(lines)


def maybe_plot(summary: dict, out_dir: Path) -> None:
    """Render standalone-readable figures.

    The story splits by family, so we plot the families separately rather than averaging them
    (which would dilute the cascade effect under the comprehension ceiling): cascade scenarios on
    *success* (where rot breaks the agent) and comprehension scenarios on *output tokens* (where rot
    just taxes generation). Plain-English condition labels, value annotations, and self-explanatory
    titles, so the charts make sense without the report. Re-reads raw.jsonl for the per-family split.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    import statistics

    raw = out_dir / "raw.jsonl"
    if not raw.exists():
        return
    rows = [json.loads(l) for l in raw.read_text().splitlines() if l.strip()]
    # Order models by capability (small → large) so "a bigger model doesn't help" reads left→right;
    # unknown names fall back to alphabetical after the known ones.
    rank = {"haiku": 0, "sonnet": 1, "opus": 2}
    models = sorted(summary["models"], key=lambda m: (rank.get(m, 99), m))
    conds = [c for c in ("C0", "C1", "C2", "C3", "Cw") if c in summary["conditions"]]
    label = {
        "C0": "No docs",
        "C1": "Stale docs",
        "C2": "Fresh docs\n(Surface)",
        "C3": "Stale docs +\nSurface report",
        "Cw": "Stale docs +\nstaleness warning",
    }
    palette = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
    color = {m: palette[i % len(palette)] for i, m in enumerate(models)}

    casc = [r for r in rows if r["scenario"].startswith("cascade-")]
    comp = [r for r in rows if not r["scenario"].startswith("cascade-")]

    def cell(sub, m, c):
        return [r for r in sub if r["model"] == m and r["condition"] == c]

    def succ_pct(sub, m, c):
        x = cell(sub, m, c)
        return 100 * sum(bool(r["ok"]) for r in x) / len(x) if x else 0.0

    def mean_out(sub, m, c):
        x = [r["output_tokens"] for r in cell(sub, m, c) if r.get("output_tokens") is not None]
        return statistics.mean(x) if x else 0.0

    def grouped(ax, sub, valfn, ylabel, *, ymax=None, fmt="{:.0f}"):
        n = len(models)
        width = 0.8 / max(n, 1)
        for i, m in enumerate(models):
            vals = [valfn(sub, m, c) for c in conds]
            offs = [j + (i - (n - 1) / 2) * width for j in range(len(conds))]
            ax.bar(offs, vals, width=width, color=color[m], label=m, edgecolor="white", linewidth=0.5)
            top = ymax or (max(vals) if vals else 1) or 1
            for off, v in zip(offs, vals):
                ax.text(off, v + top * 0.012, fmt.format(v), ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(conds)))
        ax.set_xticklabels([label.get(c, c) for c in conds], fontsize=8)
        ax.set_ylabel(ylabel, fontsize=9)
        if ymax:
            ax.set_ylim(0, ymax)
        ax.grid(axis="y", alpha=0.25, linewidth=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    panels = [("casc", casc)] * bool(casc) + [("comp", comp)] * bool(comp)
    if not panels:
        return

    # Combined overview (one panel per non-empty family).
    fig, axes = plt.subplots(1, len(panels), figsize=(5.6 * len(panels), 4.3))
    axes = [axes] if len(panels) == 1 else list(axes)
    for ax, (kind, sub) in zip(axes, panels):
        if kind == "casc":
            grouped(ax, sub, succ_pct, "Tasks the agent got right (%)", ymax=108, fmt="{:.0f}%")
            ax.set_title(
                "Code HIDDEN — agent must trust the doc\nStale docs break every model; "
                "fresh docs & the Surface report fix it",
                fontsize=9.5,
            )
        else:
            grouped(ax, sub, mean_out, "Avg tokens the agent wrote")
            ax.set_title(
                "Code VISIBLE — agent can check it\nRot doesn't cause errors, but costs extra tokens",
                fontsize=9.5,
            )
    axes[0].legend(title="model", fontsize=8, title_fontsize=8, frameon=False, loc="upper left")
    fig.suptitle("Does stale documentation hurt a coding agent?", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_dir / "overview.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Standalone hero: the cascade success chart (the single most quotable figure).
    if casc:
        fig, ax = plt.subplots(figsize=(6.6, 4.3))
        grouped(ax, casc, succ_pct, "Tasks the agent got right (%)", ymax=108, fmt="{:.0f}%")
        ax.legend(title="model", fontsize=8, title_fontsize=8, frameon=False, loc="upper left")
        ax.set_title(
            "Coding accuracy when the agent can't see the code it depends on\n"
            "A stale doc breaks every model (a bigger model doesn't help); "
            "fresh docs or Surface's drift report restore it",
            fontsize=9.5,
        )
        fig.tight_layout()
        fig.savefig(out_dir / "cascade_success.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    # Verification hero (multi-turn only): does a confident stale doc stop the agent checking?
    if casc and any("verified_hidden" in r for r in rows):

        def ver_pct(sub, m, c):
            x = [r for r in cell(sub, m, c) if "verified_hidden" in r]
            return 100 * sum(bool(r["verified_hidden"]) for r in x) / len(x) if x else 0.0

        fig, ax = plt.subplots(figsize=(6.6, 4.3))
        grouped(ax, casc, ver_pct, "Agent read the hidden dependency (%)", ymax=108, fmt="{:.0f}%")
        ax.legend(title="model", fontsize=8, title_fontsize=8, frameon=False, loc="upper right")
        ax.set_title(
            "Does a confident (stale) doc stop the agent verifying?\n"
            "With no doc the agent reads the hidden code; a stale doc suppresses the check",
            fontsize=9.5,
        )
        fig.tight_layout()
        fig.savefig(out_dir / "verification_rate.png", dpi=150, bbox_inches="tight")
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

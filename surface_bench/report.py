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


# --- Figure styling --------------------------------------------------------------------------
# Figures are rendered from the summary dict (the same Wilson/bootstrap stats the report tabulates),
# so they are faithful to the reported numbers. Honesty guards: rate charts use a zero baseline,
# every rate carries its 95% CI as error bars, no cell is dropped, and the legend sits outside the
# plot so it never overlaps bars.
_MODEL_ORDER = ["haiku", "sonnet", "opus", "gpt", "gemini"]
_PROVIDER = {"haiku": "Anthropic", "sonnet": "Anthropic", "opus": "Anthropic",
             "gpt": "OpenAI", "gemini": "Google"}
_COLOR = {"haiku": "#6BAED6", "sonnet": "#3182BD", "opus": "#08519C",
          "gpt": "#E6550D", "gemini": "#31A354"}
_COND_ORDER = ["C0", "C1", "C2", "C3", "Cw"]
_COND_LABEL = {"C0": "No docs", "C1": "Stale\ndocs", "C2": "Fresh docs\n(Surface)",
               "C3": "Stale +\nSurface report", "Cw": "Stale +\nwarning"}


def _order_models(summary):
    present = set(summary["models"])
    return [m for m in _MODEL_ORDER if m in present] + sorted(present - set(_MODEL_ORDER))


def _style(ax):
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def _legend(ax, models):
    from matplotlib.lines import Line2D

    handles = [Line2D([0], [0], marker="s", linestyle="", markersize=8, color=_COLOR.get(m, "#888"),
                      label=f"{m} ({_PROVIDER.get(m, '?')})") for m in models]
    ax.legend(handles=handles, fontsize=8, frameon=False, title="model", title_fontsize=8,
              loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0)


def _grouped_rate(ax, summary, models, field, ci_field, source, ylabel, title):
    conds = [c for c in _COND_ORDER if c in summary["conditions"]]
    n = len(models)
    width = 0.8 / max(n, 1)
    for i, m in enumerate(models):
        vals, errs, offs = [], [[], []], []
        for j, c in enumerate(conds):
            cell = summary[source][m][c]
            v = 100 * cell[field]
            lo, hi = (100 * x for x in cell[ci_field])
            vals.append(v)
            errs[0].append(max(0.0, v - lo))
            errs[1].append(max(0.0, hi - v))
            offs.append(j + (i - (n - 1) / 2) * width)
        ax.bar(offs, vals, width=width, color=_COLOR.get(m, "#888"), label=m,
               edgecolor="white", linewidth=0.5, zorder=2)
        ax.errorbar(offs, vals, yerr=errs, fmt="none", ecolor="#333", elinewidth=0.8,
                    capsize=2, zorder=3)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([_COND_LABEL.get(c, c) for c in conds], fontsize=8)
    ax.set_ylim(0, 108)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10)
    _style(ax)


def maybe_plot(summary: dict, out_dir: Path) -> None:
    """Render standalone-readable figures from the summary (no re-reading raw.jsonl).

    Always: cascade success, misled rate, and a pre-registered effects forest. Multi-turn only
    (guarded on the verification/mediation summary blocks): the verification-rate chart, the
    three-failure-modes scatter, and the H5 mediation chart.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    models = _order_models(summary)
    if not models or not summary.get("rates"):
        return

    # 1. Cascade success (hero).
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    _grouped_rate(ax, summary, models, "success", "success_ci", "rates",
                  "Tasks solved correctly (%)",
                  "Coding accuracy when the agent can't see the code it depends on\n"
                  "A stale doc breaks every model; fresh docs or Surface's report restore it "
                  "(bars = 95% Wilson CI)")
    _legend(ax, models)
    fig.tight_layout()
    fig.savefig(out_dir / "cascade_success.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 2. Misled rate (H2 — rot is worse than nothing).
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    _grouped_rate(ax, summary, models, "misled", "misled_ci", "rates",
                  "Tasks where the agent asserted the STALE claim (%)",
                  "Rot is worse than nothing: a stale doc actively misleads\n"
                  "With no doc the agent is rarely misled; a stale doc misleads the majority "
                  "(bars = 95% Wilson CI)")
    _legend(ax, models)
    fig.tight_layout()
    fig.savefig(out_dir / "misled_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 3. Cost vs accuracy — fresh docs are the cost-accuracy optimum (per model; cost from raw $).
    # Answers "why have docs if no-docs scores well?": no-docs is correct but the priciest way to be,
    # because the agent pays to rediscover the hidden dependency. C2 sits top-left (best) in each panel.
    raw_path = out_dir / "raw.jsonl"
    if raw_path.exists():
        import statistics

        rows = [json.loads(l) for l in raw_path.read_text().splitlines() if l.strip()]
        conds = [c for c in _COND_ORDER if c in summary["conditions"]]
        ccolor = {"C0": "#7F7F7F", "C1": "#C44E52", "C2": "#2CA02C", "C3": "#3182BD", "Cw": "#E6845E"}
        clabel = {"C0": "no docs", "C1": "stale", "C2": "fresh", "C3": "+report", "Cw": "+warning"}
        n = len(models)
        fig, axes = plt.subplots(1, n, figsize=(3.05 * n, 3.6), squeeze=False)
        for ax, m in zip(axes[0], models):
            for c in conds:
                cells = [r for r in rows if r["model"] == m and r["condition"] == c]
                if not cells:
                    continue
                cost = 1000 * statistics.mean(r["cost_usd"] for r in cells)  # $ per 1,000 tasks
                succ = 100 * summary["rates"][m][c]["success"]
                hi = c == "C2"
                ax.scatter([cost], [succ], s=170 if hi else 70, color=ccolor.get(c, "#888"),
                           marker="*" if hi else "o", edgecolor="black" if hi else "white",
                           linewidth=1.2 if hi else 0.6, zorder=3)
                ax.annotate(clabel.get(c, c), (cost, succ), textcoords="offset points",
                            xytext=(6, 4), fontsize=7.5, fontweight="bold" if hi else "normal")
            ax.set_title(f"{m} ({_PROVIDER.get(m, '?')})", fontsize=9)
            ax.set_xlabel("Cost per 1,000 tasks ($)", fontsize=8)
            ax.set_ylim(-6, 108)
            ax.margins(x=0.25)
            _style(ax)
        axes[0][0].set_ylabel("Tasks solved correctly (%)", fontsize=9)
        fig.suptitle("Fresh docs (★) are the cost–accuracy optimum: most accurate AND cheapest\n"
                     "No-docs is correct but pricier — the agent pays to rediscover the hidden "
                     "dependency (top-left = ideal)", fontsize=11, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.9))
        fig.savefig(out_dir / "cost_accuracy.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    # Multi-turn figures (only when verification was measured).
    ver = summary.get("verification") or {}
    has_ver = bool(ver) and all("C1" in ver.get(m, {}) for m in models)

    if has_ver:
        # 4. Verification rate (H4 hero).
        fig, ax = plt.subplots(figsize=(8.5, 4.6))
        _grouped_rate(ax, summary, models, "verification_rate", "verification_ci", "verification",
                      "Agent read the hidden dependency (%)",
                      "Does a confident (stale) doc stop the agent verifying?\n"
                      "With no doc every model checks the hidden code; a stale doc suppresses it "
                      "(bars = 95% Wilson CI)")
        _legend(ax, models)
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

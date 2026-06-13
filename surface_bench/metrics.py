"""Aggregate raw.jsonl into rates, confidence intervals, and condition deltas.

Trials are drawn *independently* per condition (same prompt, fresh stochastic completions), so
conditions are compared as unpaired proportions: Wilson intervals per rate, and a bootstrap CI on
each rate difference. No external stats dependency.
"""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

Z = 1.959963984540054  # 95%


@dataclass
class Rate:
    n: int
    k: int

    @property
    def rate(self) -> float | None:
        return self.k / self.n if self.n else None

    def wilson(self) -> tuple[float, float] | None:
        if not self.n:
            return None
        p, n = self.k / self.n, self.n
        denom = 1 + Z**2 / n
        centre = (p + Z**2 / (2 * n)) / denom
        half = (Z * math.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2))) / denom
        return (max(0.0, centre - half), min(1.0, centre + half))


def load_rows(results_dir: str | Path) -> list[dict]:
    raw = Path(results_dir) / "raw.jsonl"
    return [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]


def _samples(rows: list[dict], model: str, condition: str, field: str) -> list[int]:
    return [
        1 if r.get(field) else 0
        for r in rows
        if r["model"] == model and r["condition"] == condition
    ]


def _bootstrap_mean(xs: list[float], n_boot: int = 10000, seed: int = 0):
    if not xs:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(n_boot))
    return (sum(xs) / len(xs), means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1])


def _bootstrap_delta(a: list[float], b: list[float], n_boot: int = 10000, seed: int = 0):
    """Bootstrap CI for mean(a) - mean(b)."""
    if not a or not b:
        return None
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        ra = sum(rng.choice(a) for _ in a) / len(a)
        rb = sum(rng.choice(b) for _ in b) / len(b)
        diffs.append(ra - rb)
    diffs.sort()
    lo = diffs[int(0.025 * n_boot)]
    hi = diffs[int(0.975 * n_boot) - 1]
    return (sum(a) / len(a) - sum(b) / len(b), lo, hi)


def summarize(rows: list[dict]) -> dict:
    models = sorted({r["model"] for r in rows})
    conditions = sorted({r["condition"] for r in rows})

    rates: dict[str, dict[str, dict]] = defaultdict(dict)
    for model in models:
        for cond in conditions:
            succ = _samples(rows, model, cond, "ok")
            misled = _samples(rows, model, cond, "misled")
            sr, mr = Rate(len(succ), sum(succ)), Rate(len(misled), sum(misled))
            rates[model][cond] = {
                "n": sr.n,
                "success": sr.rate,
                "success_ci": sr.wilson(),
                "misled": mr.rate,
                "misled_ci": mr.wilson(),
            }

    # Headline deltas (success rate) per model.
    pairs = [("C2", "C1"), ("C0", "C1"), ("C3", "C1"), ("C2", "C0")]

    def delta_block(subset: list[dict], model: str) -> dict:
        out: dict[str, dict] = {}
        for hi, lo in pairs:
            bs = _bootstrap_delta(
                _samples(subset, model, hi, "ok"), _samples(subset, model, lo, "ok")
            )
            if bs is not None:
                point, ci_lo, ci_hi = bs
                out[f"{hi}-{lo}"] = {
                    "delta": point,
                    "ci": [ci_lo, ci_hi],
                    "significant": ci_lo > 0 or ci_hi < 0,
                }
        return out

    deltas = {model: delta_block(rows, model) for model in models}

    # The gradient: the same deltas sliced by complexity tier. The headline of the experiment is
    # that the Surface effect (C2-C1) *grows* as re-deriving truth from code gets more expensive.
    tiers = sorted({r.get("tier", "T0") for r in rows})
    by_tier: dict[str, dict[str, dict]] = {}
    for tier in tiers:
        sub = [r for r in rows if r.get("tier", "T0") == tier]
        by_tier[tier] = {model: delta_block(sub, model) for model in models}

    # Output-token cost. Input tokens differ by construction (doc-block size), so we track only
    # *output* tokens — where the cost of reconciling a stale doc against the code shows up.
    def out_tokens(model, cond, *, only=None):
        return [
            r["output_tokens"]
            for r in rows
            if r["model"] == model
            and r["condition"] == cond
            and r.get("output_tokens") is not None
            and (only is None or bool(r.get(only)))
        ]

    tokens: dict[str, dict[str, dict]] = defaultdict(dict)
    token_deltas: dict[str, dict[str, dict]] = defaultdict(dict)
    for model in models:
        for cond in conditions:
            allt = out_tokens(model, cond)
            correct_t = out_tokens(model, cond, only="ok")
            misled_t = out_tokens(model, cond, only="misled")
            mean = _bootstrap_mean(allt)
            tokens[model][cond] = {
                "n": len(allt),
                "mean_output": mean[0] if mean else None,
                "mean_output_ci": [mean[1], mean[2]] if mean else None,
                # The cross-tab: is a misled answer cheaper (parroted) than a correct one (reconciled)?
                "mean_output_correct": (sum(correct_t) / len(correct_t)) if correct_t else None,
                "mean_output_misled": (sum(misled_t) / len(misled_t)) if misled_t else None,
            }
        # Positive delta = the first condition spends more output tokens.
        for hi, lo in [("C1", "C2"), ("C1", "C0"), ("C1", "C3")]:
            bs = _bootstrap_delta(out_tokens(model, hi), out_tokens(model, lo))
            if bs is not None:
                point, ci_lo, ci_hi = bs
                token_deltas[model][f"{hi}-{lo}"] = {
                    "delta": point,
                    "ci": [ci_lo, ci_hi],
                    "significant": ci_lo > 0 or ci_hi < 0,
                }

    # Spend — the "I spent $X validating Surface" headline. Per (model, condition), per model,
    # and grand total, summed from the per-call cost estimates.
    def spend(rows_subset: list[dict]) -> float:
        return sum(r.get("cost_usd", 0.0) or 0.0 for r in rows_subset)

    cost = {
        "total_usd": spend(rows),
        "by_model": {m: spend([r for r in rows if r["model"] == m]) for m in models},
        "by_model_condition": {
            m: {c: spend([r for r in rows if r["model"] == m and r["condition"] == c]) for c in conditions}
            for m in models
        },
    }

    return {
        "models": models,
        "conditions": conditions,
        "tiers": tiers,
        "cost": cost,
        "rates": rates,
        "deltas": deltas,
        "by_tier": by_tier,
        "tokens": tokens,
        "token_deltas": token_deltas,
    }

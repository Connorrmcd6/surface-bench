"""Post-hoc robustness reanalysis of the confirmatory multi-turn snapshot.

These checks are EXPLORATORY additions made after the pre-registered analysis
(they were not in the frozen plan); they exist to test whether the §6
conclusions survive (a) treating scenario as a clustering unit rather than
pooling completions as independent Bernoulli trials, (b) dropping the
oracle-flagged cells, and (c) output-token truncation. They also quantify the
"any authoritative doc suppresses verification" contrast (C0-C2), which the
pre-registration did not anticipate.

Run:
    uv run python tools/reanalysis_robustness.py results/confirmatory-20260616T172420Z

Deterministic: fixed seed 20260616, 10,000 cluster-bootstrap resamples.
"""
import json
import random
import collections
import sys

SEED = 20260616
B = 10000
MODELS = ["haiku", "sonnet", "opus", "gpt", "gemini"]
CONDS = ["C0", "C1", "C2", "C3", "Cw"]


def load(path):
    rows = [json.loads(l) for l in open(f"{path}/raw.jsonl")]
    scen = sorted({r["scenario"] for r in rows})
    idx = collections.defaultdict(list)
    for r in rows:
        idx[(r["model"], r["condition"], r["scenario"])].append(r)
    return rows, scen, idx


def rate(rs, key):
    return sum(1 for r in rs if r[key]) / len(rs) if rs else float("nan")


def pooled(idx, model, cond, scens, key):
    return rate([r for s in scens for r in idx[(model, cond, s)]], key)


def cluster_boot_delta(idx, scen, model, a, b, key="ok"):
    """95% CI for rate(a)-rate(b), resampling SCENARIOS with replacement."""
    obs = pooled(idx, model, a, scen, key) - pooled(idx, model, b, scen, key)
    n = len(scen)
    deltas = []
    for _ in range(B):
        samp = [random.choice(scen) for _ in range(n)]
        ra = rate([r for s in samp for r in idx[(model, a, s)]], key)
        rb = rate([r for s in samp for r in idx[(model, b, s)]], key)
        deltas.append(ra - rb)
    deltas.sort()
    return obs * 100, deltas[int(0.025 * B)] * 100, deltas[int(0.975 * B)] * 100


def main(path):
    random.seed(SEED)
    rows, scen, idx = load(path)
    out = []
    p = out.append
    p(f"# Robustness reanalysis — {path}\n")
    p(f"Rows: {len(rows)} · scenarios: {len(scen)} · "
      f"cluster bootstrap: {B} resamples, seed {SEED}.\n")

    # ---- #1 scenario-clustered bootstrap ----
    p("## 1. Scenario-clustered bootstrap (resampling scenarios, not completions)\n")
    p("Success-delta point estimate with 95% scenario-clustered CI (pp).\n")
    pairs = [("H1 C2-C1", "C2", "C1"), ("H3 C3-C1", "C3", "C1"),
             ("H6 C3-Cw", "C3", "Cw"), ("C2-C0 (marginal)", "C2", "C0")]
    for label, a, b in pairs:
        p(f"**{label}**")
        for m in MODELS:
            o, lo, hi = cluster_boot_delta(idx, scen, m, a, b)
            sig = "excludes 0" if (lo > 0 or hi < 0) else "**CROSSES 0**"
            p(f"- {m}: {o:+.1f} [{lo:+.1f}, {hi:+.1f}] {sig}")
        p("")

    # ---- #2 any-doc suppresses verification ----
    p("## 2. Verification suppression: fresh doc (C0-C2) vs stale (C0-C1)\n")
    p("| model | C0 | C1 | C2 | C3 | Cw | C0-C1 (H4) | C0-C2 |")
    p("|---|---|---|---|---|---|---|---|")
    for m in MODELS:
        v = {c: pooled(idx, m, c, scen, "verified_hidden") * 100 for c in CONDS}
        p(f"| {m} | {v['C0']:.0f} | {v['C1']:.0f} | {v['C2']:.0f} | "
          f"{v['C3']:.0f} | {v['Cw']:.0f} | {v['C0']-v['C1']:+.0f} | "
          f"{v['C0']-v['C2']:+.0f} |")
    p("")

    # ---- #3 leave-them-out ----
    flagged, detail = set(), []
    for m in MODELS:
        for s in scen:
            c2 = rate(idx[(m, "C2", s)], "ok")
            c1m = rate(idx[(m, "C1", s)], "misled")
            if c2 < 0.90:
                flagged.add((m, s)); detail.append(f"{m}/{s}: C2={c2:.0%}")
            if c1m == 0.0:
                flagged.add((m, s)); detail.append(f"{m}/{s}: C1 never misleads")
    p(f"## 3. Leave-them-out: drop {len(flagged)} oracle-flagged cells\n")
    for d in sorted(detail):
        p(f"- {d}")
    p("")

    def pooled_delta(model, a, b, drop):
        scens = [s for s in scen if (model, s) not in drop]
        ra = rate([r for s in scens for r in idx[(model, a, s)]], "ok")
        rb = rate([r for s in scens for r in idx[(model, b, s)]], "ok")
        return (ra - rb) * 100, len(scens)

    for label, a, b in [("H1 C2-C1", "C2", "C1"), ("H3 C3-C1", "C3", "C1"),
                        ("H6 C3-Cw", "C3", "Cw")]:
        p(f"**{label}** (full → flagged-excluded)")
        for m in MODELS:
            full, _ = pooled_delta(m, a, b, set())
            excl, nsc = pooled_delta(m, a, b, flagged)
            p(f"- {m}: {full:+.1f} → {excl:+.1f} (n_scen {nsc})")
        p("")

    # ---- #4 ceiling / truncation ----
    p("## 4. Output-token ceiling hits & answer mode (per cell)\n")
    p("| model | cond | turn≥1024 % | text_answer % | forced % |")
    p("|---|---|---|---|---|")

    def ceil_hit(r):
        return any(t[1] >= 1024 for t in r.get("per_turn_tokens", []))
    for m in MODELS:
        for c in CONDS:
            rs = [r for s in scen for r in idx[(m, c, s)]]
            ch = sum(ceil_hit(r) for r in rs) / len(rs) * 100
            ta = sum(r["stop_reason"] == "text_answer" for r in rs) / len(rs) * 100
            fa = sum(r["stop_reason"] == "forced_answer" for r in rs) / len(rs) * 100
            p(f"| {m} | {c} | {ch:.1f} | {ta:.1f} | {fa:.1f} |")
    p("")

    text = "\n".join(out)
    with open(f"{path}/robustness.md", "w") as f:
        f.write(text)
    print(text)
    print(f"\nWrote {path}/robustness.md")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         "results/confirmatory-20260616T172420Z")

# Haiku multi-turn re-run — post-fix results & oracle clearance

**Run:** `results/20260616T060356Z/` · multi mode, `max_turns=8`, N=10, `temperature=1.0`,
`max_tokens=1024`, surf 0.6.2 · **haiku only** · 13 cascade scenarios × 5 conditions = **650 completions, $5.34, 0 errors**.

This is the post-fix re-run of [`HAIKU_MULTI_PILOT_ANALYSIS.md`](HAIKU_MULTI_PILOT_ANALYSIS.md)
(`results/20260615T200423Z/`), with `cascade-idempotency-window-qa` now excluded from multi mode.
Its purpose was gate step 3: **confirm the oracle clears on a real model before freezing.**

Regenerate:

```sh
uv run python -m surface_bench.report results/20260616T060356Z
uv run python -m surface_bench.oracle results/20260616T060356Z
```

---

## 1. Verdict: oracle effectively clears — safe to freeze and run the full matrix

Down from **4 oracle warnings to 1**, and the surviving warning is a model output-format miss, not a
fixture defect (see §3). Every pre-registered hypothesis holds, and the headline (H4/H5) is *stronger*
than the first pilot.

### Headline (the non-tautological core)

| Hypothesis | Result | Status |
|---|---|---|
| **H4** verification suppression: C0 → C1 | 100% → 21% = **+79 pp** [+72, +86] | ✓ stronger than pilot (+69) |
| **H5** within-C1 mediation | verifiers **52%** correct (n=27) vs non-verifiers **7%** (n=103) | ✓ clean |

With no doc the agent *always* reads the hidden file (100%); a confident stale doc collapses that to
21%. Within C1, the few who still verified were 7× more likely to be right.

### Full confirmatory family (all Holm ✓ except the n.s. control)

| | Contrast | Delta | Holm |
|---|---|---|---|
| H1 | C2 − C1 (fresh − stale) | +78 pp [+70, +85] | ✓ |
| H2 | misled C1 vs C0 | 78% vs 0% | ✓ |
| H3 | C3 − C1 (surf report recovers) | +52 pp [+42, +62] | ✓ |
| H6 | C3 − Cw (the *fix*, not mere suspicion) | +46 pp [+35, +57] | ✓ |
| — | Cw − C1 (bare warning alone) | +6 pp [−4, +15] | ✗ (expected null: a warning with no code doesn't help) |

Rates per cell (n=130): C0 78% / C1 16% (misled 78%) / C2 94% / C3 68% (misled 24%) / Cw 22% (misled 68%).

### Spend
$5.34 (haiku). Consistent with the pilot's $5.80 over the slightly larger scenario set.

---

## 2. Oracle output (1 warning, exit 0) — and how it changed

```
- C2-fresh low: cascade-quota-batcher-code / haiku = 70% (< 90%)
```

| Previously flagged (pilot) | Now | Status |
|---|---|---|
| idempotency-window-qa (C1 never misleads) | **excluded from multi** | ✅ resolved |
| signal-threshold-code (C2 = 80%) | **C2 = 100%** | ✅ cleared |
| validate-guard-ts-code (C2 = 80%) | **C2 = 90%** | ✅ cleared |
| quota-batcher-code (C2 = 80%) | C2 = 70% | ⚠️ see §3 — format miss, not a defect |

Per-cell breakdown for the three previously-watched scenarios (n=10 each; `ver` = read hidden dep):

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| quota-batcher-code | ok5 mis0 ver10 | ok0 mis9 ver0 | ok7 mis0 ver0 | ok10 mis0 ver10 | ok5 mis2 ver8 |
| signal-threshold-code | ok10 mis0 ver10 | ok7 mis2 ver0 | ok10 mis0 ver1 | ok7 mis2 ver10 | ok4 mis5 ver1 |
| validate-guard-ts-code | ok8 mis0 ver10 | ok0 mis10 ver0 | ok9 mis0 ver1 | ok0 mis9 ver5 | ok0 mis10 ver3 |

---

## 3. The one surviving warning: `cascade-quota-batcher-code` C2 = 70%

**Diagnosis: output-format compliance misses by haiku — not doc rot, not logic, not a fixture bug.** ✅ no fixture fix

All three C2 failures are the *same* failure: the model derived the right capacity but didn't follow
the output contract. Evidence from the raw rows:

- The failing solutions contain `capacity = WINDOW_LIMIT + 1` and the comment
  `# So with WINDOW_LIMIT=10, the per-window capacity is 10 + 1 = 11` — i.e. **capacity is correct (11)**,
  and the batching loop (`min(capacity, remaining)` + remainder) is correct.
- Yet the grade `detail` is **`"no FILE blocks in output"`**: the model wrote `FILE: code/throttle.py`
  followed by the code **without the required ```` ``` ```` fence**, so the harness extracted no file
  and scored it neither `ok` nor `misled`.

So the C2 shortfall is the model occasionally dropping the markdown fence, not failing the task. The
drift signal is fully intact: **C1 misled 9/10, C2 never misled, C3 = 100%.**

- **Action: no fixture change.** Two non-blocking options:
  1. Leave it — expect ≥90% on stronger models (format compliance improves with capability).
  2. *(harness robustness, optional)* make `grade_code` extraction tolerant of a `FILE:` marker
     followed by an unfenced body. This would help all code scenarios, not just this one, and is a
     parser leniency change — **not** a scenario edit, so it doesn't touch the manipulation.

---

## 4. Notes for the full matrix

- **validate-guard C3 = 0% persists** (ver5: agents read the corrected code *and* the hidden file,
  then wrote the stale rule anyway). Same genuine doc-trust effect documented in the pilot — a feature
  of the result, not a defect.
- **signal-threshold stale effect is still mild** (C1 misled only 2/10; 7/10 still correct). Valid but
  the softest fixture; worth watching whether C1-misled strengthens on more capable models.
- **Mediation is slightly lower than the pilot** (verifiers 52% vs 67%), dragged by validate-guard's
  C3 behaviour; still a clean 52% vs 7% split.

## 5. Recommendation

Oracle is effectively clean (the lone warning is a model format miss with the doc-trust signal
intact). **Proceed to freeze:** tag `PREREGISTRATION.md` / `PAPER.md`, then run the full 5-model
multi matrix. Optionally apply the harness extraction-leniency tweak (§3, option 2) first — it would
lift quota-batcher's C2 ceiling and remove the cosmetic oracle warning, but it is not required and
must stay a parser change, never a scenario edit.

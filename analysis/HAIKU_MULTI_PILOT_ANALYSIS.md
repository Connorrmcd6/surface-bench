# Haiku multi-turn pilot — results analysis & flagged-scenario triage

**Run:** `results/20260615T200423Z/` · multi mode, `max_turns=8`, N=10, `temperature=1.0`,
`max_tokens=1024`, surf 0.6.2 · **haiku only** · 14 cascade scenarios × 5 conditions = **700 completions, $5.80, 0 errors**.

Regenerate the numbers below with:

```sh
uv run python -m surface_bench.report results/20260615T200423Z
uv run python -m surface_bench.oracle results/20260615T200423Z
```

---

## 1. Verdict: worth pursuing — run the other four models after fixing/triaging the flagged fixtures

This was the **primary (multi-turn) mode** — the centerpiece the §5 single-shot pilot could not
test. Every pre-registered hypothesis landed in the predicted direction and survived Holm.

### Headline (the non-tautological core)

| Hypothesis | Result | Status |
|---|---|---|
| **H4** verification suppression: C0 → C1 | 99% → 31% = **+69 pp** [+61, +76] | ✓ strong |
| **H5** within-C1 mediation | verifiers **67%** correct (n=43) vs non-verifiers **5%** (n=97) | ✓ clean |

The agent had the hidden file available to read in every cell. A confident **stale** doc cut its
verification rate from near-universal (99%) to ~a third (31%), and the agents who *didn't* verify
were almost all misled. That is the mechanism the study is built to demonstrate, and on haiku it is
real and large.

### Full confirmatory family (all Holm ✓ except the n.s. control)

| | Contrast | Delta | Holm |
|---|---|---|---|
| H1 | C2 − C1 (fresh − stale) | +70 pp [+61, +78] | ✓ |
| H2 | misled C1 vs C0 | 71% vs 0% | ✓ |
| H3 | C3 − C1 (surf report recovers) | +51 pp [+41, +61] | ✓ |
| H6 | C3 − Cw (the *fix*, not mere suspicion) | +46 pp [+35, +56] | ✓ |
| — | Cw − C1 (bare warning alone) | +5 pp [−5, +16] | ✗ (as expected: a warning with no code doesn't help) |

Note the multi-turn dynamic range is *more* informative than the saturated single-shot pilot:
C1 success is 24% (not 0%) and C0 is 78% (not ~0%), because the agent can now sometimes verify —
which is exactly what makes the mediation story legible.

### Cost to finish the matrix

haiku multi = $5.80. Scaling by §5 single-shot ratios (sonnet ≈3×, opus ≈5.5× haiku), plus
gpt + gemini, the full 5-model multi matrix is roughly **$80–130**.

---

## 2. Oracle output (4 warnings, exit 0 — warnings, not failures)

```
- C1 never misleads: cascade-idempotency-window-qa / haiku — drift may not be load-bearing
- C2-fresh low:      cascade-quota-batcher-code      / haiku = 80% (< 90%)
- C2-fresh low:      cascade-signal-threshold-code   / haiku = 80% (< 90%)
- C2-fresh low:      cascade-validate-guard-ts-code  / haiku = 80% (< 90%)
```

Per-cell breakdown for the four (n=10 each; `ver` = read the hidden dep before answering):

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| idempotency-window-qa | ok10 mis0 ver10 | ok10 mis0 ver10 | ok10 mis0 ver10 | ok10 mis0 ver10 | ok10 mis0 ver10 |
| quota-batcher-code | ok9 mis0 ver10 | ok1 mis8 ver1 | ok8 mis0 ver1 | ok10 mis0 ver10 | ok3 mis5 ver5 |
| signal-threshold-code | ok10 mis0 ver10 | ok6 mis4 ver1 | ok8 mis0 ver0 | ok7 mis2 ver9 | ok6 mis2 ver3 |
| validate-guard-ts-code | ok4 mis0 ver10 | ok0 mis10 ver0 | ok8 mis0 ver1 | ok0 mis10 ver2 | ok0 mis9 ver0 |

---

## 3. Per-scenario triage

### 3.1 `cascade-idempotency-window-qa` — **real issue: non-load-bearing in multi mode** ⚠️ fix/drop

**What the oracle saw:** C1 never misleads (0 misled in every condition).

**Why:** the agent **verifies 100% of the time in every condition, including C1** (ver10 across the
board). It always opens `code/payments/idempotency.py`, sees `is_duplicate` returns `False`, and
answers correctly regardless of what the doc says. The stale doc exerts **no** suppression here, so
the cell measures nothing for the H4/H5 headline.

This is *not* a leak or grader-polarity bug — the task text is neutral and the agent genuinely reads
the truth. It's that, for this QA scenario, haiku's default behaviour is to verify, so a stale doc
can't suppress what the agent was always going to do.

- **Diagnosis:** genuine non-load-bearing drift **in multi mode** (it was fine in single-shot, where
  there's no option to verify).
- **Action:** either (a) **drop from the multi matrix** (record the choice in `run.json`, not chosen
  by results), or (b) make the verification more costly/less inviting so the doc becomes load-bearing.
  Simplest honest move: drop it from multi and keep it for single mode only.
- **Files:** `scenarios/cascade-idempotency-window-qa/{task.md,meta.toml,grader/}`

### 3.2 `cascade-quota-batcher-code` — **not a fixture bug; haiku capability slip** ✅ no fix

**What the oracle saw:** C2-fresh = 80%.

**Why:** the fresh hub is unambiguous — it states the inclusive bound and literally says *"at
`WINDOW_LIMIT = 10` the limiter admits 11."* Yet **C3 (which appends the surf report's literal
`if count <= self.limit:`) = 100%**, while **C2 (prose only) = 80%**. The two C2 misses are haiku
failing to translate the off-by-one *prose* into code — given the literal corrected code it gets it
right every time.

- **Diagnosis:** model-capability noise on an off-by-one, not an authoring defect. Expect ≥90% on
  sonnet/opus.
- **Action:** **no fix.** Re-check the cell on a stronger model before touching the fixture.

### 3.3 `cascade-signal-threshold-code` — **not a fixture bug; capability slip + mildly weak stale effect** ✅ no fix (watch)

**What the oracle saw:** C2-fresh = 80%.

**Why:** the fresh hub is clear ("alerts on a **drop** … `curr - prev < 0`"). C0 = 100%, C2 = 80% —
two slips translating the sign-flip into `should_page`. Secondary observation: the **stale effect is
weak** here (C1 only 4/10 misled, 6/10 still correct), so this fixture is a softer demonstration than
the others.

- **Diagnosis:** capability slip on a sign-flip; weak-ish but valid drift.
- **Action:** **no fix.** Re-check on stronger models. If C1-misled stays low across models,
  consider strengthening the drift so the stale claim is more clearly load-bearing.

### 3.4 `cascade-validate-guard-ts-code` — **not a bug; arguably the strongest demonstration** ✅ no fix

**What the oracle saw:** C2-fresh = 80%.

**Why this one is the most interesting:** look at a failing **C3** row (agent had the surf report
*and* read the hidden file, `verified=True`, turns=4):

```ts
export function acceptedNames(names: string[]): string[] {
  // Per documentation: isValidName returns true for NON-EMPTY names of at most 50 characters
  return names.filter(name => name.length > 0 && name.length <= 50);
}
```

The agent **read the corrected code, then wrote the stale rule anyway, citing "Per documentation."**
The grader correctly scored this `misled`. That is a clean, genuine doc-trust failure — not a
grader-polarity or TS type-strip bug. C3 = 0% and Cw = 0% here are *real* (the confident stale prose
beat both the surf report and the agent's own reading), which is a striking result, not a defect.

The C2 = 80% flag is, again, two capability slips (C0 is only 40% — haiku struggles to mirror the
empty-name rule into a filter even when it reads the code), so the fixture is simply *hard for
haiku*, not mis-authored.

- **Diagnosis:** valid fixture; low C0/C2 are haiku difficulty, low C3 is a genuine (and strong)
  effect.
- **Action:** **no fix.** Re-check C2 on stronger models; expect it to clear 90%.

---

## 4. Recommended next steps (in order)

1. **idempotency-window-qa:** decide drop-from-multi vs. strengthen; record in `run.json`. *(only true fix needed)*
2. **Re-run haiku** and confirm the oracle’s three "C2-fresh low" warnings are model-capability, not
   authoring — i.e. verify they clear ≥90% on **sonnet/opus** (cheap to check with a 2-model,
   3-scenario spot run before the full matrix).
3. If all three clear on stronger models and idempotency is resolved, **tag `PREREGISTRATION.md`**
   and run the full 5-model (haiku/sonnet/opus/gpt/gemini) multi matrix.
4. Optionally strengthen `signal-threshold` drift if C1-misled stays weak across models.

**Do not carry the flagged fixtures unresolved into the confirmatory run** — at minimum resolve
idempotency-window-qa, since a permanently-null H4/H5 cell shouldn't sit inside the headline family.

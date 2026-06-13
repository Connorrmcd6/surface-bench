# Snapshot provenance — 2026-06-13 full pilot matrix

Curated, committed snapshot of the first full Surface agent-impact pilot (milestone "Empirical
validation of Surface", issue #101). Force-added past `bench/.gitignore` (which ignores `results/`).

## Configuration

- **Models:** haiku (`claude-haiku-4-5-20251001`), sonnet (`claude-sonnet-4-6`), opus (`claude-opus-4-8`)
- **Trials:** N = 10 per (scenario × condition × model)
- **Scenarios:** all 11 — 4 `cascade-*` (hidden dependency) + 7 comprehension
- **Conditions:** C0 code-only · C1 stale doc · C2 fresh doc · C3 stale doc + `surf check` report
- **Total:** 1320 calls, **0 errors**, estimated spend **$13.98** (haiku $1.49 · sonnet $4.21 · opus $8.28)
- **Code:** branched from `main` after #114 merged; the per-request timeout in `models.py`
  (committed alongside this snapshot) was in effect for the resume below.

## Assembly note (honest accounting)

The dataset was assembled from **two runs at the same prompts/grading**:

1. The original matrix run completed 8 of 11 scenarios (960 rows) before a single API request hung
   with no client-side timeout, stalling the run. All completed rows were preserved.
2. After adding a 120 s per-request timeout + retries to the Anthropic client, the 3 unfinished
   scenarios (`refresh-replay-premise-qa`, `refresh-single-use-qa`, `retry-budget-code`) were
   re-run fresh (360 rows) and merged with the preserved 960.

The merge is clean: every scenario has exactly 120 rows (10 × 4 × 3), no duplicates, 0 errors. Only
the network timeout differed between the two runs — prompts, scenarios, graders, and the `surf`
binary were identical.

## Headline result (see `report.md` / `summary.json` for full CIs)

**Cascade family (the dependency is hidden — the agent knows it only by doc):** on **all three
models**, a stale doc (C1) yields **0% success / 100% misled**, a fresh doc (C2) yields **100%
success**, and the `surf` report (C3) recovers to **90% (haiku) / 100% (sonnet, opus)**. H1 = +100pp
on every model — **a more capable model is *not* more robust to rot** when it cannot see the code.

**Comprehension family (the code is visible):** success ceilings near 100% across models, but a
stale doc still costs **+57 to +107 extra output tokens** vs a fresh one on every model — the
wasted-token tax of rot you *can* see.

Files: `raw.jsonl` (all 1320 rows) · `summary.json` (machine-readable rates, CIs, deltas) ·
`report.md` (full authored write-up: overview, hypotheses, methodology, prompts, results,
interpretation, learnings, future work) · `success_{haiku,sonnet,opus}.png` · `run.json` (original
run metadata).

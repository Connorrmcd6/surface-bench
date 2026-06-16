# Provenance — confirmatory multi-turn matrix

This is the frozen confirmatory snapshot for §6 of `PAPER.md`. It is the centerpiece dataset of the
study, run **after** the pre-registration was git-tagged.

## Freeze / pre-registration

- **Pre-registration tag:** `prereg-v2-multi` (annotated), recorded in `PREREGISTRATION.md` and §0 of
  the paper. The tag commit predates all data below.
- **`surf --version`:** `surf 0.6.2`.

## Configuration

- **Mode:** multi-turn agent loop, `max_turns = 8`, read-only tools (`read_file`, `grep`, `list_dir`,
  `final_answer`).
- **Sampling:** `temperature = 1.0`, `max_tokens = 1024`, `trials (N) = 10` per cell.
- **Conditions:** C0, C1, C2, C3, Cw.
- **Scenarios:** 13 cascade scenarios. `cascade-idempotency-window-qa` was **pre-excluded from multi
  mode** (recorded in `run.json` `excluded_scenarios`) as non-load-bearing — the agent verifies it in
  100% of trials regardless of the doc — a choice fixed before the run, not chosen by results.
- **Models (5, 3 providers):** `haiku` (claude-haiku-4-5-20251001), `sonnet` (claude-sonnet-4-6),
  `opus` (claude-opus-4-8), `gpt` (gpt-5.4), `gemini` (gemini-3.5-flash, run with `thinking_budget=0`
  for single-completion-budget parity).

## How this snapshot was assembled

Each model was run **separately**, one at a time, into its own `results/run-<model>/` directory (so a
mid-run failure of one model could never corrupt another), then the per-model `raw.jsonl` files were
**concatenated** into this directory and a combined `run.json` (union of the five model specs) was
written. `report` + `oracle` were then run on the merged directory.

| Model | Source run timestamp | Rows |
|---|---|---|
| haiku  | 20260616T083438Z | 650 |
| gpt    | 20260616T101102Z | 650 |
| gemini | 20260616T105612Z | 650 |
| sonnet | 20260616T123339Z | 650 |
| opus   | 20260616T150036Z | 650 |
| **merged** | 20260616T172420Z | **3,250** |

- **3,250 graded completions, 0 errors, 0 excluded (errored) cells.** Each model contributes exactly
  650 rows (13 scenarios × 5 conditions × 10 trials); no duplicates.
- **Spend:** $62.16 total (opus $28.59, sonnet $13.33, gemini $8.99, gpt $5.95, haiku $5.29),
  estimated from per-row token usage at the prices in `run.json`.

## Oracle

`surface_bench.oracle` reported 9 warnings across the 65 scenario×model cells (5 × "C2-fresh < 90%",
clustered on TypeScript scenarios and gemini; 4 × "C1 never misleads", strong models immune to
specific easy scenarios). Per the pre-registered rule (§4.3) these are **flagged and reported, not
dropped**; they are isolated cells and every model's aggregate H1–H6 decision is unchanged with them
included. See `report.md` §"Per-scenario success rate" and §6.5 of `PAPER.md`.

## Re-grading / regeneration

`raw.jsonl` preserves the raw model outputs. To regenerate `summary.json`, `report.md`, and the
figures offline without re-spending:

```sh
uv run python -m surface_bench.report results/confirmatory-20260616T172420Z
uv run python -m surface_bench.oracle  results/confirmatory-20260616T172420Z
```

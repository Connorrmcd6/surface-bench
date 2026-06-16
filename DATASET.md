# surface-bench — dataset card

A pre-registered, provider-agnostic benchmark measuring how **documentation accuracy** changes an
LLM coding agent's task performance, and through what mechanism. This card describes the released
data so other researchers can reuse it. The study itself is written up in [`PAPER.md`](PAPER.md).

- **License:** CC BY 4.0 (data, scenarios, research docs) — see [`LICENSE-DATA`](LICENSE-DATA). The
  harness code is MIT — see [`LICENSE`](LICENSE).
- **Citation:** see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository" button).
- **No PII.** All data are model completions on synthetic, author-written fixtures.

## What's included

Two committed snapshots under `results/`, each fully re-gradeable from its raw model outputs:

| Snapshot | Mode | Models | Completions | Errors |
|---|---|---|---|---|
| [`results/2026-06-13-pilot-full-matrix/`](results/2026-06-13-pilot-full-matrix/) | single-shot (pilot) | 3 Claude | 1,320 | 0 |
| [`results/confirmatory-20260616T172420Z/`](results/confirmatory-20260616T172420Z/) | multi-turn (confirmatory) | 5 across Anthropic / OpenAI / Google | 3,250 | 0 |

The confirmatory run is the centerpiece (pre-registered, git-tagged `prereg-v2-multi`). Each snapshot
carries a `PROVENANCE.md` documenting exactly how it was produced.

Each snapshot directory contains:

- `raw.jsonl` — one JSON object per graded completion (the primary data; see schema below).
- `summary.json` — computed aggregates (rates, deltas, tokens, verification, per-scenario/tier).
- `run.json` — full run provenance (model ids + prices, trials, temperature, max_tokens, mode,
  max_turns, conditions, scenarios, `surf --version`, and any pre-declared `excluded_scenarios`).
- `report.md`, `*.png` — the standalone human-readable write-up and figures.

## Conditions

Every cell holds the **same code, task, and model**; only the documentation block changes:

| | Context shown to the agent |
|---|---|
| `C0` | code only (no doc) |
| `C1` | code + **stale** doc (true at T0; code has moved to T1) |
| `C2` | code + **fresh** doc (matches T1) |
| `C3` | code + stale doc + genuine `surf check` divergence report (includes corrected code) |
| `Cw` | code + stale doc + a content-free "may be outdated" warning |

## `raw.jsonl` schema

One object per completion. Fields common to all rows:

| Field | Type | Meaning |
|---|---|---|
| `scenario` | str | scenario id (e.g. `cascade-quota-batcher-code`) |
| `task_type` | str | `code` or `qa` |
| `tier` | str | difficulty tier (`T1` buried, `T2` premise, …) |
| `condition` | str | `C0`–`Cw` (see above) |
| `model` | str | short model name (`haiku`, `sonnet`, `opus`, `gpt`, `gemini`) |
| `trial` | int | 0-based repetition index |
| `output` | str | the model's raw final text (re-gradeable) |
| `input_tokens` / `output_tokens` | int | token usage |
| `cost_usd` | float | estimated cost at the prices in `run.json` |
| `ok` | bool | **success** — produced the current (T1) answer |
| `misled` | bool | **misled** — asserted the stale (T0) claim |
| `detail` | str | grader detail (e.g. `correct test passed`) |
| `parsed` | obj | parser output (applied files / parsed verdict) |

Multi-turn rows additionally carry:

| Field | Type | Meaning |
|---|---|---|
| `mode` | str | `multi` (single-shot pilot rows omit this) |
| `turns` | int | agent turns used |
| `stop_reason` | str | why the loop ended (e.g. `final_answer`) |
| `tool_calls` | list | the read-only tool calls made |
| `verified_hidden` | bool | whether the agent read the hidden dependency before answering |
| `per_turn_tokens` | list | per-turn token counts |

Failed cells (none in the released snapshots) would carry an `error` field instead of grades.

## Loading

```python
import json
rows = [json.loads(l) for l in open("results/confirmatory-20260616T172420Z/raw.jsonl")]

# e.g. success rate for stale docs (C1) per model
from collections import defaultdict
agg = defaultdict(list)
for r in rows:
    if r["condition"] == "C1":
        agg[r["model"]].append(r["ok"])
print({m: round(sum(v)/len(v), 3) for m, v in agg.items()})
```

Regenerate `summary.json`, `report.md`, and figures offline (no model calls, no spend):

```sh
uv sync
uv run python -m surface_bench.report results/confirmatory-20260616T172420Z
uv run python -m surface_bench.oracle  results/confirmatory-20260616T172420Z
```

## Provenance & integrity

- Pre-registration was git-tagged (`prereg-v2-multi`, `surf 0.6.2`) **before** the confirmatory run;
  hypotheses, conditions, metrics, and the analysis plan are frozen in
  [`PREREGISTRATION.md`](PREREGISTRATION.md).
- Grading is fully deterministic (hidden unit tests / fixed-format verdict rubrics) — **no LLM
  judge**. Ground truth for cascade scenarios is derived by probing the real hidden dependency.
- Per-snapshot `PROVENANCE.md` records assembly, row counts, spend, and any oracle flags.

## Limitations

Curated synthetic fixtures (not real repositories), a read-only agent loop (no edit/run/test thrash),
Python and TypeScript only. See [`PAPER.md`](PAPER.md) §8 for the full threats-to-validity treatment.

## Citing this dataset / minting a DOI

Use [`CITATION.cff`](CITATION.cff) for citation metadata. To mint a permanent, citable DOI:

1. Enable the repository in [Zenodo](https://zenodo.org/) (GitHub integration, one-time).
2. Cut a GitHub Release; Zenodo automatically archives that release and issues a DOI.
3. Add the DOI to the `doi:` field in `CITATION.cff` and a DOI badge to `README.md`.

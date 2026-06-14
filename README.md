# surface-bench — operator manual

Empirically measuring how much **documentation accuracy** changes an agent's task performance — the
gap [Surface](../README.md) exists to protect. Surface doesn't make an agent smarter; it stops docs
silently rotting. So its value to an agent equals the performance delta between working from **fresh**
docs and **rotted** docs, plus whether *surfacing* the drift recovers the loss. This bench measures
those deltas directly, using drift of exactly the kind `surf check` catches (flipped operators,
dropped guards, changed constants, reordered keys).

This is the single place to start when you (or a future agent) pick this up cold. It covers **what the
experiment is, how to run it, how to read the results, how to author scenarios, and the sharp edges.**
Lives in the Surface repo but has no inbound dependency on the Rust core — it only *consumes* the
`surf` binary's output — so it can be extracted later.

> **Companion docs:** [`PREREGISTRATION.md`](PREREGISTRATION.md) (the frozen hypotheses + analysis
> plan for the headline run), [`ABC_CHECKLIST.md`](ABC_CHECKLIST.md) (benchmark-rigor self-audit),
> [`scenarios/CHECKLIST.md`](scenarios/CHECKLIST.md) (how to author one scenario), and the committed
> v1 write-up at [`results/2026-06-13-pilot-full-matrix/report.md`](results/2026-06-13-pilot-full-matrix/report.md).

---

## 1. The experiment in one screen

Same code + same task in every run; **only the documentation block changes**. There are five
conditions:

| | Context shown to the agent | Represents |
|---|---|---|
| **C0** | code only (no doc) | baseline |
| **C1** | code + **stale** doc (true at T0, code moved to T1) | the ungoverned world |
| **C2** | code + **fresh** doc (matches T1) | the Surface-governed world |
| **C3** | code + stale doc + real `surf check --format json` report | "just surface the drift" |
| **Cw** | code + stale doc + a generic "may be outdated" warning (no corrected code) | control: is it the *fix* or just *suspicion*? |

And two run **modes**:

- **single** (v1): one prompt → one completion. Cheap, reproducible, the original pilot.
- **multi** (v2, the centerpiece): a **multi-turn agent loop** with **read-only** tools
  (`read_file`, `grep`, `list_dir`, `final_answer`). The agent can *choose* to read the hidden
  dependency the doc describes. This is what makes the headline non-tautological — see §4.

### Hypotheses

| | Claim | Read on |
|---|---|---|
| **H1** | C2 > C1 — accuracy beats rot (the core value) | success rate |
| **H2** | C1 < C0 — rotted docs are *worse than nothing* | misled rate |
| **H3** | C3 ≈ C2 — surfacing drift recovers the loss | success rate |
| **H4** | verification_rate(C1) < verification_rate(C0) — a confident stale doc **suppresses verification** | verification rate (multi only) |
| **H5** | within C1, agents that read the hidden dep are correct; those that don't are misled | mediation (multi only) |
| **H6** | C3 > Cw — recovery is Surface's *corrected code*, not mere suspicion | success rate |

### Two scenario families

- **Cascade** (the headline): the agent edits/answers about a **visible** thing whose correctness
  depends on a **hidden dependency** (listed in `meta.toml` `hidden_paths` — present in `code/` for
  grading and for `surf` to seal a real divergence, but withheld from the prompt). The dependency
  has drifted from what the stale doc says, so the doc is the agent's only (single-shot) or
  *optional* (multi-turn) window onto the truth. `cascade-*` scenarios.
- **Comprehension**: the drifted code *and* its contradicting doc are both visible. The model can
  just re-read the code, so success ceilings near 100% — useful for the **token-tax** story (a stale
  doc costs extra generation to reconcile), not the success story.

---

## 2. Setup

The harness env is managed with [uv](https://docs.astral.sh/uv/) (the committed `uv.lock` pins it so
the spend figures are reproducible). Code-edit graders run under the *same* interpreter `uv run`
selects — no `python3`-on-PATH guessing.

```sh
# from repo root: build the real surf binary (author.py + the C3 report need it)
cargo build --release                       # provides target/release/surf

cd bench
uv sync                                      # base deps (anthropic)
uv sync --extra dev                          # + pytest (to run the test suite)
uv sync --extra plots                        # + matplotlib (report figures)
uv sync --extra providers                    # + openai, google-genai (cross-provider runs)
```

**Toolchains the graders need at run time** (only when those scenarios are actually graded):

- **Python** — always (via `sys.executable`).
- **Node ≥ 22.18** on PATH — for TypeScript code scenarios (`node --test`; that release strips TS
  types at load, so no `npm install`/`tsc`). uv does not manage Node; install it separately.

**API keys** (only for the providers you select): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY` (or `GOOGLE_API_KEY`). The convenience env file `~/.surface-bench.env` is sourced
per command in practice (`set -a; source ~/.surface-bench.env; set +a`).

---

## 3. Running it

The pipeline is four commands. **Everything except `run` against a real provider is free/offline.**

```sh
# (a) RUN the matrix -> results/<ts>/{raw.jsonl, run.json}
uv run python -m surface_bench.run --models mock                      # offline pipeline check, no key
uv run python -m surface_bench.run --models haiku --mode single --trials 10
uv run python -m surface_bench.run --models haiku --mode multi --trials 10 --max-turns 8

# (b) REPORT -> results/<ts>/{summary.json, report.md, *.png}
uv run python -m surface_bench.report results/<ts>

# (c) ORACLE — post-run sanity tripwires (exits non-zero if any fire)
uv run python -m surface_bench.oracle results/<ts>
```

**CLI flags** (`run`): `--models <names…>` (subset of `config.toml` models; default all),
`--scenarios <ids…>`, `--conditions C0 C1 C2 C3 Cw`, `--trials N`, `--mode {single,multi}`,
`--max-turns N` (multi), `--out <dir>`, `--config <path>`. Config defaults live in `config.toml`
(`trials`, `temperature`, `max_tokens`, `mode`, `max_turns`, and a `[models.<name>]` block per
model with `provider`, `model_id`, and `input_per_mtok` / `output_per_mtok` pricing).

**Providers:** `provider = "mock" | "anthropic" | "openai" | "gemini"`. Mock needs no key and is the
offline workhorse; in `--mode multi` it scripts a canned answer so the whole loop runs for free.

### The matrix size (and why you stage spend)

`#scenarios × #conditions × #models × N`. Multi mode multiplies each cell by the number of agent
turns *and* re-sends the growing transcript each turn, so it is **much** more expensive than single.
**Always stage:** `mock` → one scenario × each provider (smoke the tool round-trip) → cascade-only
multi at small N (pilot the verification metric) → the full matrix. Gate each stage on the oracle
(§5) passing. Cost levers: `--max-turns` cap, tiered `--trials` (e.g. N=10 cascade / N=5
comprehension), and dropping comprehension from multi mode (it doesn't test verification).

---

## 4. Reading the results

`run` writes **`raw.jsonl`** (one row per completion — the source of truth; grading can be re-run
offline without re-spending) and **`run.json`** (the run's parameters). `report` turns those into
`summary.json` (machine-readable) + `report.md` (the human read) + figures.

**Per-row fields** (multi-only fields absent in single rows): `scenario, task_type, tier, condition,
model, trial, mode, output, input_tokens, output_tokens, cost_usd, ok, misled, detail, parsed` and,
for multi: `turns, stop_reason, tool_calls, verified_hidden, per_turn_tokens`.

**The metrics, and what each tells you:**

- **success rate** (`ok`) — got the current (T1) answer. The H1/H3/H6 axis. Deterministic: code
  scenarios run hidden tests; QA scenarios parse a `VERDICT:` line against a rubric. **No LLM judge.**
- **misled rate** (`misled`) — asserted the *stale* (T0) claim. The H2 axis: a rotted doc doesn't
  just fail to help, it *causes* the wrong answer.
- **verification_rate** (multi) — did the agent read/grep a `hidden_path` before answering? The
  **headline of the agentic track** (H4). `verified_then_correct` is its validity check (reading the
  truth should rescue you).
- **output tokens** — generation cost. Input tokens differ by construction (doc-block size) so are
  ignored; output tokens carry the token-tax signal in the comprehension family.
- **cost_usd** — estimated spend (tokens × `config.toml` prices). The report's total is for relative
  comparison; your provider console invoice is authoritative.

**Statistics:** rates carry 95% **Wilson** intervals; condition deltas use a 95% **bootstrap** CI
*and* a bootstrap p-value, with **Holm–Bonferroni** applied across the whole success-delta family
(the report flags `(Holm ✓/✗)` per delta). CI-significance is the headline; Holm is the conservative
cross-check. The report also slices deltas **by tier** (the difficulty gradient) and **by scenario**
(catches one broken fixture hiding in a family average).

**`report.md` sections:** Spend · the gradient (C2−C1 by tier) · **Verification** (multi: the H4
deltas + H5 mediation) · per-model rate tables + deltas (with Holm flags) · output-token tables +
deltas · per-scenario success. **Figures:** `overview.png`, `cascade_success.png`, and (multi)
`verification_rate.png` — the "does a stale doc stop the agent checking?" hero chart.

---

## 5. The oracle (sanity tripwires)

`python -m surface_bench.oracle results/<ts>` is a cheap post-run gate that catches authoring/harness
bugs **before** they reach a write-up (the failure mode that bit us in issue #113). It exits non-zero
(so it can gate CI / a staged run) if, per scenario × model:

- **C2-fresh < 90%** — with a *fresh* doc the task must be solvable; a low cell means the scenario is
  mis-authored (leaked stale value, broken grader, impossible task), not a real effect.
- **a cascade C1 never misleads** — if a stale doc never produces the wrong answer, the drift isn't
  load-bearing and the scenario measures nothing.

The mock can't satisfy these (it doesn't actually solve scenarios), so run the oracle on **real**
outputs.

---

## 6. Layout

```
bench/
  config.toml                models, trials, temperature, mode, max_turns, per-model pricing
  PREREGISTRATION.md         frozen hypotheses + analysis plan for the headline run
  ABC_CHECKLIST.md           benchmark-rigor self-audit (arXiv 2507.02825)
  surface_bench/
    run.py                   the matrix runner (single + multi); writes raw.jsonl + run.json
    prompts.py               assembles (system, user) per condition; hides hidden_paths
    models.py                provider adapters: complete() (single) + step() (multi, tool-use);
                             Anthropic / OpenAI / Gemini + Mock; neutral Step/ToolCall types
    agent.py                 run_agent() — the multi-turn loop over the read-only tools
    tools_runtime.py         read-only tool surface (read_file/grep/list_dir/final_answer) + sandbox
    grade_qa.py              VERDICT-line rubric grader (QA)
    grade_code.py            FILE-block overlay + hidden-test grader (code)
    metrics.py               rates, Wilson/bootstrap CIs, Holm, verification, by_tier, by_scenario
    report.py                summary.json + report.md + figures
    oracle.py                post-run tripwires
  tools/
    author.py                seal a scenario's hub hashes + emit genuine surf_report.json
    validate_scenario.py     grader-polarization self-test (offline, no spend)
  scenarios/
    CHECKLIST.md             how to author one scenario
    <id>/                    meta.toml · task.md · hub_stale.md · hub_fresh.md · surf_report.json
                             code/ (T1) · .author/code_t0/ (T0 overlay) · .author/solution_{correct,stale}.*
                             grader/ (rubric.toml | grader.toml + tests/)
  tests/                     offline pytest (tools, agent loop, adapters, metrics, scenario polarity)
  results/<timestamp>/       raw.jsonl · run.json · summary.json · report.md · *.png  (gitignored,
                             except committed snapshots like 2026-06-13-pilot-full-matrix)
```

---

## 7. Authoring a scenario (summary — full steps in `scenarios/CHECKLIST.md`)

A cascade scenario clones `scenarios/cascade-quota-batcher-code/`. The loop:

1. Pick a **load-bearing** drift: name an input where T0 and T1 give *different* outputs (else the
   doc carries no weight and the bench measures nothing).
2. Write `code/` (T1, the visible file stubbed) + `.author/code_t0/` (only the changed files, T0) +
   `hub_stale.md`/`hub_fresh.md` (placeholder `hash: 000000000000`) + a **neutral** `task.md` +
   the grader + `.author/solution_{correct,stale}.*` reference solutions.
3. `python tools/author.py scenarios/<id>` — seals the hub hashes against the real binary and emits
   `surf_report.json`; **fails loudly if the stale hub doesn't actually diverge.**
4. `python tools/validate_scenario.py scenarios/<id>` — runs the live graders on the two reference
   solutions and proves they **discriminate** (correct → ok & not misled; stale → not ok & misled).
5. `--models mock` run + `oracle` to confirm the pipeline + tripwires.

**Two rules with teeth:**

- **Graders probe the real hidden dependency** for ground truth — never hardcode the T1 value.
  `check_misled` hardcodes the *stale* value.
- **Neutrality** (the #113 lesson): the stale value appears *only* in `hub_stale.md` — never in
  `task.md` or the visible code, and never a "the doc may be wrong" hint. A leak re-introduces the
  doc-trust bias the neutral system prompt is designed to remove.

---

## 8. Sharp edges (read before authoring or debugging)

- **`surf` alpha-renames identifiers when hashing.** A drift expressed only as a *named-constant
  swap* (e.g. `ROUND_HALF_EVEN` → `ROUND_HALF_UP`) is **invisible** to `surf check` — the two hash
  identically. A detectable drift must change a **literal, operator, or structure** (a number, a
  string, `<`→`<=`, an added/removed statement, a reordered call). `author.py` fails with "expected
  a 'changed' divergence" if you trip this — redesign the drift, don't fight the hasher.
- **`author.py` seals only the *first* anchor's hash.** Multi-anchor hubs (a genuine T3 "multi-claim"
  scenario) need a small tooling change to seal every anchor; until then keep hubs single-anchor.
- **Read-only tools by design.** The multi-turn agent can read but not edit or run code. Giving it a
  test runner would let it brute-force ground truth and wash out the doc-trust signal we measure. A
  full edit/run "thrash" loop is deliberately deferred future work.
- **Don't stack PRs.** Scenario PRs are additive and independent — open each against `main` directly.
  (A stacked PR once merged into its base branch instead of `main` and silently lost its content.)
- **Spend is in the *run*, not the docs/tooling.** `author.py`, `validate_scenario.py`, `report`,
  `oracle`, the test suite, and any `mock` run cost nothing. Only `run` against a real provider does.

---

## 9. Reproducibility

`uv.lock` pins the Python env. `run.json` records every parameter (models + ids, trials,
temperature, max_tokens, mode, max_turns, conditions, scenarios, `surf --version`). `raw.jsonl`
preserves raw outputs so grading/metrics re-run offline. To reproduce a committed snapshot, check out
the repo at its tag, `cargo build --release`, `cd bench && uv sync`, and re-run `report` on the
snapshot dir (it regenerates `summary.json` + figures from the frozen `raw.jsonl`).

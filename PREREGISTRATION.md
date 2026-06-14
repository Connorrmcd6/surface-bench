# Pre-registration — Surface agent-impact benchmark (v2 / multi-turn)

**Status:** to be **frozen and git-tagged before the headline run.** This file states the
hypotheses, design, metrics, and analysis *in advance* so the result can't be accused of HARKing
(hypothesizing after results are known) or of cherry-picking an analysis. Nothing below is decided
by looking at outcomes. Operating instructions are in [`README.md`](README.md).

> **Freeze gate.** Tag this only once: (a) the scenario set is final (all `cascade-*` PRs merged),
> (b) `python tools/author.py --all` and `python tools/validate_scenario.py --all` are green across
> the set, and (c) a full `--models mock` run + `python -m surface_bench.oracle` is clean. Record
> the tag and the `surf --version` here when frozen: `__TBD__`.

## 1. Question

Does keeping documentation accurate (what Surface enforces) change an agent's task performance, and
*through what mechanism*? Surface's value to an agent = the performance gap between working from
fresh vs rotted docs, plus whether surfacing the drift recovers it.

## 2. Conditions (the only thing that varies)

Same code + same task + same model in every cell; only the documentation block changes:
**C0** code only · **C1** code + stale doc · **C2** code + fresh doc · **C3** code + stale doc + real
`surf check --format json` report · **Cw** code + stale doc + a generic "may be outdated" warning
(no corrected code). Run in **multi mode** (the agent has read-only `read_file`/`grep`/`list_dir`
tools and may choose to verify) as the primary design; **single mode** is run as a secondary,
cheaper comparison.

## 3. Hypotheses (confirmatory)

- **H1 — accuracy beats rot:** success(C2) > success(C1).
- **H2 — rot is worse than nothing:** misled(C1) > misled(C0).
- **H3 — surfacing drift recovers it:** success(C3) ≈ success(C2) (and ≫ C1).
- **H4 — a confident stale doc suppresses verification:** verification_rate(C1) < verification_rate(C0).
- **H5 — the harm flows through skipped verification (mediation):** within C1, success among rows
  that verified > success among rows that did not; verifiers are correct, non-verifiers misled.
- **H6 — recovery is the corrected code, not mere suspicion:** success(C3) > success(Cw).

Direction is pre-specified for every hypothesis. Anything not listed here (e.g. per-provider
contrasts, tier gradients, token-cost deltas) is **exploratory** and will be reported as such.

## 4. Metrics (pre-defined)

- **success** — `ok`: the agent produced the current (T1) answer. Code scenarios: hidden tests that
  probe the real dependency. QA scenarios: a `VERDICT:` line matched against a fixed rubric. **No LLM
  judge.**
- **misled** — `misled`: the agent asserted the stale (T0) claim.
- **verification_rate** (multi only) — the agent called `read_file`/`grep` on a path matching the
  scenario's `hidden_paths` glob *before* `final_answer`. Computed from the logged `verified_hidden`
  per row. `verified_then_correct` (success among verifiers) is its validity check.
- **output tokens** and **cost** — secondary (token-tax + spend), exploratory.

## 5. Models, scale, sampling (pre-specified)

- **Models:** `haiku`, `sonnet`, `opus` (Anthropic) + `gpt` (OpenAI) + `gemini` (Google). Exact
  `model_id`s and prices are pinned in `config.toml` at freeze time and copied into `run.json`.
- **Trials (tiered):** N = 10 per cell for the **cascade** family (the headline); N = 5 for the
  **comprehension** family (success-ceilinged — kept only for the token story). Comprehension may be
  omitted from multi mode entirely (it doesn't test verification); that choice is recorded in
  `run.json`, not chosen by results.
- **temperature = 1.0** (stochasticity is part of what we measure); **max_turns = 8**;
  `max_tokens = 1024`.

## 6. Analysis plan (pre-specified)

- Rates reported with 95% **Wilson** intervals.
- Each hypothesis tested as an unpaired difference of proportions with a 95% **bootstrap** CI and a
  bootstrap two-sided p-value (10,000 resamples, fixed seed).
- **Holm–Bonferroni** correction applied across the family of confirmatory success-delta tests
  (every model × pre-registered pair). A hypothesis is **confirmed** if its CI excludes 0 **and** it
  survives Holm; reported as suggestive if CI-significant but not Holm-significant.
- H5 (mediation) reported as the within-C1 success split (verified vs not) per model.
- Per-scenario and per-tier breakdowns reported for transparency (exploratory).

## 7. Exclusions / data handling (pre-specified)

- A cell that errors (API failure) is logged with `error` and excluded from rates; the count of
  excluded cells is reported. No silent retries beyond the client's built-in retry.
- The oracle (§ README) must be clean on the real run: any scenario failing C2-fresh ≥ 90% or (for
  cascade) C1-misled > 0 is treated as a **fixture defect** and is flagged; whether to drop it is
  decided by the pre-stated oracle rule, not by whether it helps the result.

## 8. Stopping rule

The matrix runs to completion (fixed N above). No data-dependent stopping, no N top-ups chosen by
looking at significance. If a stage smoke (mock → per-provider → small-N pilot) reveals a *harness*
bug, it is fixed and the affected stage re-run; the confirmatory full run begins only after this file
is tagged.

## 9. What this does and does not assess

Assesses: whether documentation accuracy changes single-shot and multi-turn task outcomes on curated
cascade fixtures across five models, and whether the effect is mediated by verification. Does **not**
assess: real-repository generalization (curated fixtures by design — see deferred #109), an
edit/run/test agent loop (tools are read-only by design), or non-English / languages beyond Python
and TypeScript.

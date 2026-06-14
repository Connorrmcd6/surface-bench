# ABC checklist — benchmark-rigor self-audit

A self-audit against the **Agentic Benchmark Checklist** (ABC) from *Establishing Best Practices for
Building Rigorous Agentic Benchmarks* (Zhu et al., NeurIPS 2025 D&B; arXiv **2507.02825**). The ABC
groups failure modes into **task validity** (can the task be solved as specified?), **outcome
validity** (does the grader actually measure success — no shortcuts, no false pass/fail?), and
**reporting**. The paper found *all 10* benchmarks it audited had reporting gaps; this file is our
attempt not to be one of them. Item ids follow the paper's grouping.

Legend: ✅ satisfied · ⚠️ partial / by-design limitation · n/a not applicable to this benchmark.

## Task validity

| Item | How this benchmark addresses it |
|---|---|
| **T.1** tool/version specificity | Model `model_id`s pinned in `config.toml`, copied into `run.json`; `surf --version` recorded. Python env pinned by `uv.lock`. ✅ |
| **T.2/T.3** API availability / interruption handling | Per-request 120 s timeout + bounded retries; a cell that still fails is logged with `error` and **excluded** from rates (not counted as a failure). ✅ |
| **T.4** clean state between tasks | Each grade runs in a **fresh temp workspace** (`grade_code`) / each multi-turn trial in a **fresh sandbox** (`tools_runtime.scenario_sandbox`). No cross-task leakage. ✅ |
| **T.5** isolate agent from ground truth | The drifted dependency is withheld from the prompt (`hidden_paths`); graders compute ground truth separately by probing the real dependency. The agent never sees the grader. ✅ |
| **T.6** freeze environment at release | Scenario set frozen + git-tagged at pre-registration (see `PREREGISTRATION.md` freeze gate). ✅ |
| **T.7/T.8** verify ground-truth annotations | Ground truth is **derived from the real code**, not hand-annotated: code graders import and probe the hidden dependency; QA rubrics encode the T1 behaviour the committed code implements. ✅ |
| **T.9** oracle/reference solution | Every scenario ships `.author/solution_correct.*` and `solution_stale.*`; `tools/validate_scenario.py` runs the live graders on both and proves they discriminate, offline, before any spend. ✅ |
| **T.10** inspect pilot outliers | Staged rollout (`mock` → per-provider smoke → small-N pilot → full) with the oracle as a tripwire; the v1 pilot's outlier (a leaked stale value) was caught this way (#113). ✅ |

## Outcome validity

| Item | How this benchmark addresses it |
|---|---|
| **O.a** semantic-equivalence / redundant-word robustness | QA grading parses a **fixed `VERDICT:` field format** (regex per field) rather than free-text matching; "last match wins" tolerates the model restating the format. Code grading runs real tests, so wording is irrelevant. ✅ |
| **O.b.2/O.b.3** no trivial success (list-all / empty answer) | Code: an empty or non-compiling answer fails the hidden test. QA: a missing/garbled `VERDICT` parses as neither correct nor misled (not a pass). ✅ |
| **O.d.1** manually verify test cases | Each grader's correct/misled tests are validated by `validate_scenario.py` against the reference solutions; the **misled** test must pass on the stale solution and fail on the correct one (and vice-versa). ✅ |
| **O.f.2** eliminate non-determinism in tests | Graders are deterministic (no clocks/network/randomness in the checked logic; fixed probe inputs). ✅ |
| **O.h.1** specify output format | `task.md` states the exact contract: a `FILE: <path>` block (code) or a `VERDICT: …` line (QA). ✅ |
| **O.h.2** tasks resistant to guessing | The reason multi-turn is the centerpiece: in single-shot a hidden value is only knowable from the doc, so "follow the stale doc" is partly rational. Multi-turn lets the agent *verify*, removing the tautology. QA verdicts use **two fields** to cut a 50/50 guess. ⚠️ (single-shot cascade is guess-resistant only because the value is genuinely unknowable without the doc — stated as a limitation) |
| **O.i.1** metric correlates with the construct | `verified_then_correct` validates the verification metric (reading the truth should rescue the answer); the misled metric directly encodes "asserted the stale claim". ✅ |

## Reporting

| Item | How this benchmark addresses it |
|---|---|
| **R.1/R.2** open data + eval code | The entire harness, scenarios, graders, and reference solutions are in this repo. `raw.jsonl` is preserved per run. ✅ |
| **R.3/R.4** contamination | Scenarios are bespoke fixtures, not scraped; the drift values live only in `hub_stale.md`. (Frontier models may have seen similar idioms — noted as residual risk.) ⚠️ |
| **R.5/R.6** state the capability assessed | `PREREGISTRATION.md` §9 states exactly what is and isn't assessed. ✅ |
| **R.7** mitigation for unavoidable flaws | The neutral system prompt + neutral `task.md` rules (#113 lesson) mitigate doc-trust bias; the oracle mitigates fixture defects. ✅ |
| **R.8/R.9** quantify limitation impact | Per-scenario and per-tier breakdowns expose any single-fixture or single-difficulty artifact. ✅ |
| **R.10** statistical significance | Wilson intervals, bootstrap CIs + p-values, **Holm–Bonferroni** across the confirmatory family. ✅ |
| **R.11** interpretation guidance | `README.md` §4 explains what each metric means; `PREREGISTRATION.md` separates confirmatory from exploratory. ✅ |
| **R.12/R.13** baselines/controls | **C0** (no-doc baseline) and **Cw** (warning-only control) isolate, respectively, the value of accurate prose and whether recovery is Surface's *fix* vs generic suspicion. ✅ |

## Known limitations (disclosed, per R.7)

- **Curated fixtures, not real repositories** (external validity); a real-OSS case study is deferred
  (#109).
- **Read-only agent loop** — no edit/run/test "thrash"; deferred by design.
- **Languages:** Python + TypeScript only.
- **`author.py` seals only the first anchor**, so all current scenarios are single-anchor (no genuine
  T3 multi-claim); a tooling follow-up would lift this.

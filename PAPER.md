# Does documentation accuracy change LLM-agent performance?

### A pre-registered, provider-agnostic benchmark of documentation drift

**Author:** Connor McDonald
**Affiliation / artifact:** [`surface-bench`](https://github.com/Connorrmcd6/surface-bench) · companion tool: [Surface](https://github.com/Connorrmcd6/surface)
**Draft date:** 2026-06-15
**Status:** working paper

> **Reading note.** This study is **pre-registered**: the hypotheses, conditions, metrics, and
> analysis plan below were frozen *before* the confirmatory run (see `PREREGISTRATION.md`, to be
> git-tagged at the freeze gate — tag `__TBD__`, `surf 0.6.2`; the preliminary pilot in §5 used
> `surf 0.6.1`, which produces byte-identical scenario seals). The paper reports **real preliminary
> results** from a single-shot pilot (§5) and reserves clearly-marked slots — tagged
> **`[RESULTS PENDING]`** / **`[HEADLINE PENDING]`** — for the confirmatory **multi-turn** matrix
> (§6), which is the centerpiece of the study and has **not yet been run**. Every number that
> appears in §5 is drawn from the committed snapshot `results/2026-06-13-pilot-full-matrix/`; no
> confirmatory figure is reported until the headline run lands.

---

## Abstract

Software documentation rots: code moves, prose does not. LLM coding agents are unusually exposed to
this rot because they often treat documentation as ground truth — especially for parts of a codebase
they cannot, or do not, read directly. We ask a single, falsifiable question: **does keeping
documentation accurate change an agent's task performance, and through what mechanism?** We isolate
*documentation accuracy* as the only manipulated variable across five matched conditions (code only;
code + a stale doc; code + a fresh doc; code + a stale doc plus an automated drift report; and code +
a stale doc plus a generic "may be outdated" warning), holding the code, task, model, and sampling
fixed. Grading is fully deterministic — hidden unit tests for code-edit tasks and a fixed-format
verdict rubric for question-answering tasks — with **no LLM judge**. The benchmark is built to the
Agentic Benchmark Checklist (ABC; Zhu et al., 2025) -- [# where is the link?] and is pre-registered to forestall HARKing and
analysis cherry-picking.

In a **single-shot pilot** (3 Claude models, 4 conditions, 1,320 graded completions, 0 errors), when
the drifted dependency was *hidden* from the agent — the realistic large-codebase case — a stale doc
made **every model wrong on 100% of tasks** and confidently *misled* (asserted the stale claim) on
100% of tasks, while **a more capable model was no more resistant** than a weaker one. Accurate docs
restored 100% success, and handing the agent the automated drift report recovered nearly all of the
loss. Where the code was *visible*, rot did not break correctness but imposed a consistent token tax.

The confirmatory study extends this to a **multi-turn agentic** setting in which the agent has
read-only tools (`read_file`, `grep`, `list_dir`) and may *choose* to verify the hidden dependency —
removing the "follow the only available source" tautology — across five models from three providers.
Its headline test is whether a confident stale doc **suppresses verification**: `[HEADLINE PENDING]`.

---

## 1. Introduction

### 1.1 The problem: documentation rot meets autonomous readers

Documentation drift is the silent gap between what a codebase *does* and what its docs *say*. An
operator changes from `<` to `<=`, a default page size drops from 50 to 25, an allow-list becomes a
block-list — and the surrounding prose, the design note, the docstring, the wiki page, keeps
describing the world as it was. Human engineers tolerate this because they routinely distrust docs
and re-read code. LLM coding agents are different in two ways that make drift more dangerous, not
less:

1. **They consume docs as ground truth.** A doc placed in context is, to a model, just more authoritative-looking text. Absent a reason to doubt it, the model will act on it. -- [# how do you know?]
2. **They often cannot see the relevant code.** In a real repository the file that actually implements a behavior is frequently *not* in the agent's context window — it is a transitive dependency, hidden behind an interface the agent only knows by its documentation. -- [# again how do you know?]

When both hold, a stale doc is not a minor annoyance; it is the agent's *only* window onto a behavior
that has changed underneath it. The agent then does exactly what it was asked — using a fact that is
no longer true.

This failure mode is recognized in production practice, not only in the lab. Industry accounts of
*context poisoning* name *context rot* — "information becomes outdated but remains in your knowledge
base" — as a primary cause of degraded LLM output, observing that once stale content enters the
context window "the LLM references it as truth, creating cascading errors" (Murúa, 2026) -- [# add link]. This study
turns that qualitative observation into a controlled, quantified measurement.

### 1.2 The intervention under test

[Surface](https://github.com/Connorrmcd6/surface) is a deterministic documentation-drift gate: given
anchored claims in docs and the code they point at, `surf check` reports when an anchored claim no
longer matches its code. Surface does **not** make an agent smarter; it stops docs *silently*
rotting. Its value to an agent is therefore a measurable quantity:

> the performance gap between an agent working from **accurate** docs and one working from **rotted**
> docs, plus whether **surfacing** the drift (rather than merely fixing the docs) recovers the loss.

This benchmark measures that quantity directly, using drift of exactly the kind `surf check` catches
— a flipped operator, a changed constant, an inverted condition, a dropped guard.

### 1.3 The precise claim, and what would falsify it

We do not claim "docs matter." We make a graded, falsifiable set of claims (the pre-registered
hypotheses of §4): that accurate docs beat rotted docs on task success; that rotted docs are *worse
than no docs at all* on the rate at which the agent is actively misled; that surfacing the drift
recovers the loss; that a confident stale doc *suppresses* the agent's own verification behavior; that
the resulting harm flows through skipped verification; and that recovery comes from the *corrected
code* in the drift report, not from mere suspicion. Each has a pre-specified direction. A null or
reversed result on any of them is reportable and would falsify that specific claim.

### 1.4 Contributions

- **A controlled, single-variable benchmark** of documentation accuracy for coding agents, where the
  only thing that varies across conditions is the documentation block.
- **A "cascade" scenario design** that reproduces the realistic failure shape — a *hidden* dependency
  whose behavior has drifted — and a "comprehension" family that isolates the token-cost story.
- **Fully deterministic grading** (hidden tests / fixed-format verdicts, no LLM judge) with ground
  truth derived from the real code, not hand annotation.
- **A pre-registered, ABC-compliant protocol** with oracle tripwires, multiplicity control, and a
  transparent confirmatory/exploratory split.
- **Provider-agnostic generalization**: the same scenarios run across Anthropic, OpenAI, and Google
  models, testing whether "a more capable model is no more rot-resistant" holds beyond one vendor.
- **A multi-turn agentic track** in which the agent can choose to verify, making the headline result
  non-tautological and letting us measure *verification suppression* as the mechanism.

---

## 2. Background and related work

### 2.1 Agentic benchmark rigor

Agentic benchmarks are easy to get subtly wrong: tasks that are unsolvable as specified, graders that
pass on trivial or empty answers, ground truth that leaks, non-deterministic tests, and reporting that
over-claims capability. Zhu et al. (*Establishing Best Practices for Building Rigorous Agentic
Benchmarks*, NeurIPS 2025 Datasets & Benchmarks; arXiv 2507.02825) catalogue these failure modes as
the **Agentic Benchmark Checklist (ABC)**, grouped into *task validity*, *outcome validity*, and
*reporting*. We adopt ABC as a design constraint and provide a per-item self-audit in
`ABC_CHECKLIST.md`; §3 and §8 of this paper map our design choices onto its items.

### 2.2 Pre-registration and construct validity

Two threats are endemic to benchmark write-ups. *HARKing* (hypothesizing after results are known)
lets a study present whatever pattern emerged as if it had been predicted. *Analysis cherry-picking*
lets a study choose, post hoc, the slice or test that happens to be significant. Pre-registration —
fixing hypotheses, conditions, metrics, and the analysis plan in advance, then git-tagging them
before the confirmatory run — neutralizes both. We pre-register direction for every confirmatory
hypothesis and label everything else exploratory (§4).

### 2.3 How this differs from capability benchmarks

Most coding benchmarks vary the *model* (or the agent scaffold) and hold the task fixed, asking "how
capable is the system?" We invert that: we hold the model fixed and vary the *quality of the
information* it is given, asking "how much does an information-quality defect (doc rot) move outcomes,
and can a tool that surfaces the defect recover them?" The headline is therefore **not** a capability
ranking; indeed, a central finding is that capability does *not* buy resistance to this defect.

### 2.4 Context-poisoning defenses, and where this study sits

A growing body of production-oriented work addresses *context poisoning* at the **retrieval stage** —
controlling which documents enter the context window. Murúa (2026), for example, mitigates context
rot in RAG pipelines with temporal filters (e.g., restrict to documents updated within the last
six months), metadata boosting (prefer version- or deployment-specific docs), and hybrid lexical +
semantic search. These defenses are **orthogonal and upstream** to what we study: they decide *what
gets retrieved*. Our benchmark measures agent behavior when a drifted doc is *already* in context,
and tests a *drift-detection* remedy (Surface) rather than a recency filter. The distinction matters
because recency is a weak proxy for correctness: a doc can be recently edited and still wrong because
the **code moved underneath it** — precisely the case our cascade scenarios isolate, and one a
`last_updated`-based filter cannot catch.

---

## 3. Methodology

### 3.1 Conditions — the only thing that varies

Every cell of the matrix uses the **same code, the same task, and the same model**; only the
documentation block in the prompt changes. There are five conditions:

| | Context shown to the agent | Represents |
|---|---|---|
| **C0** | code only (no doc) | baseline |
| **C1** | code + **stale** doc (true at T0, code has moved to T1) | the ungoverned world |
| **C2** | code + **fresh** doc (matches T1) | the Surface-governed world |
| **C3** | code + stale doc + real `surf check --format json` report | "just surface the drift" |
| **Cw** | code + stale doc + a generic "may be outdated" warning (no corrected code) | control: is it the *fix* or just *suspicion*? |

Each scenario has a current, drifted state (**T1**) and a pre-drift state (**T0**). The stale doc
truthfully described T0; the code has since moved to T1. The C3 report is **genuine** `surf check`
output — the documentation hubs are sealed against the real `surf` binary by `tools/author.py`, not
mocked — and it includes the corrected `new_code`. Cw strips that corrected code and replaces it with
a content-free "this may be outdated" note, so that C3 − Cw isolates whether recovery comes from the
*fix* Surface supplies or merely from making the agent *suspicious*.

### 3.2 Two run modes, and why multi-turn is the centerpiece

- **Single mode (secondary).** One prompt → one completion. Cheap and reproducible; this is the mode
  of the pilot in §5. Its limitation is a tautology: when the drifted dependency is hidden, the doc is
  the agent's *only* source of truth, so "follow the stale doc" is partly rational, and the effect can
  be dismissed as true-by-construction.
- **Multi mode (primary / centerpiece).** A multi-turn agent loop (`max_turns = 8`) with a
  **read-only** tool surface — `read_file`, `grep`, `list_dir`, and `final_answer`. A per-trial
  sandbox contains `code/` **including the hidden dependency**, which the prompt still withholds. The
  agent may therefore *choose* to open the dependency and verify the doc's claim. This removes the
  tautology: a rational, diligent agent could always be right, so any residual harm from a stale doc
  must come from the agent *declining to verify*. That is the non-tautological core of the study.

Tools are deliberately **read-only**: giving the agent a test runner would let it brute-force ground
truth and wash out the doc-trust signal we are trying to measure. A full edit/run/test "thrash" loop —
which would let us price the *compounding* cost of rot — is deferred future work.

### 3.3 Two scenario families

- **Cascade (the headline).** The agent edits or answers about a **visible** thing whose correctness
  depends on a **hidden dependency**. The dependency's source lives in `code/` (so `surf` can seal a
  real divergence and the grader can run the agent's output against reality) but is withheld from the
  prompt via a `hidden_paths` glob in `meta.toml`. The dependency has drifted from what the stale doc
  says, so in single mode the doc is the agent's *only* window onto the truth, and in multi mode it is
  an *optional* one (the agent can read the dependency if it chooses). This is the realistic
  context-rot shape.
- **Comprehension.** The drifted code *and* its contradicting doc are both visible. The model can
  simply re-read the code, so success ceilings near 100% — these scenarios are weak for the success
  story but useful for the **token-tax** story: a stale doc costs extra generation to reconcile
  against visible code.

### 3.4 Worked example — `cascade-quota-batcher-code`

The agent sees `throttle.py` and is asked to implement `plan_batches(total)`, which must split queued
requests into batches sized to a rate limiter's **per-window capacity**. The limiter
(`FixedWindowLimiter`, configured `WINDOW_LIMIT = 10`) lives in a package whose source is **not in the
checkout** (`hidden_paths = ["code/limiter/*.py"]`), so the capacity is knowable only from its doc.

The drift: the limiter's admission guard moved from `count < limit` to `count <= limit`, so its true
per-window capacity for `WINDOW_LIMIT = 10` is **11**, not 10.

- **C1 (stale doc)** asserts the capacity is *exactly* N — "at `WINDOW_LIMIT = 10` the limiter admits
  10." An agent that trusts it batches at 10 (**wrong**, and *misled*).
- **C2 (fresh doc)** asserts the inclusive bound — "admits N+1 … at `WINDOW_LIMIT = 10` the limiter
  admits 11." An agent batches at 11 (**correct**).
- **C3** keeps the stale prose but appends the `surf` report, whose `new_code` shows
  `if count <= self.limit:` — the only window onto the truth when the file is hidden.
- **Cw** keeps the stale prose and appends a generic "this documentation may be outdated" note with no
  corrected code.

The task text itself is **neutral**: it asks the agent to "determine the limiter's true per-window
capacity" and never states either the stale or the fresh value. The grader derives the expected batch
size from the *real* hidden limiter, so the test stays honest regardless of what either doc claims.

### 3.5 Prompt construction and neutrality

The prompt is a `(system, user)` pair. The system prompt is deliberately minimal and **persona-free**:

```
Use the files and documentation provided to do the task below.
```

There is no "you are an expert engineer" framing (which primes skeptical, diligent behavior and biases
*against* a stale-doc effect) and **no precedence** declared between docs and code. This mirrors how
people actually prompt agents: paste or tag some files, maybe a doc, ask for the change.

The user turn has a fixed anatomy: a `## Codebase` section (cascade scenarios omit the hidden
dependency here); a `## Project documentation` section carrying the stale or fresh hub (omitted
entirely in C0); for C3, an `## Automated documentation check` section carrying the genuine
`surf check --format json` output; and a `## Task` section stating the goal and the exact output
contract.

**Neutrality is enforced** (a lesson from a pilot failure, issue #113): the stale value appears *only*
in the stale hub — never in `task.md`, never in the visible code, and never as a "the doc may be wrong"
hint. A leak re-introduces exactly the doc-trust bias the neutral system prompt is designed to remove.

### 3.6 Deterministic grading and metrics

Grading is fully deterministic — **there is no LLM judge**.

- **Code-edit scenarios.** The agent returns whole files in `FILE: <path>` blocks. The harness
  overlays them onto a fresh copy of `code/` and runs two hidden checks: a `correct` check (passes iff
  the T1 behavior is implemented → **success**) and a `misled` check (passes iff the T0 behavior is
  implemented → **misled**). Cascade graders import and probe the *real hidden dependency* to derive
  ground truth; they never hardcode the fresh value. (The `misled` check hardcodes the *stale* value.)
- **QA scenarios.** The agent ends with a fixed-format `VERDICT: <field>=<value>; …` line. A per-field
  regex rubric adjudicates `correct` (matches T1) vs `misled` (matches the stale T0 claim). "Last
  match wins" tolerates the model restating the format; a missing or garbled verdict parses as neither
  (it is not a pass).

Metrics per cell:

- **success** (`ok`) — produced the current (T1) answer. The H1/H3/H6 axis.
- **misled** (`misled`) — asserted the *stale* (T0) claim. The H2 axis: a rotted doc doesn't merely
  fail to help, it *causes* the wrong answer.
- **verification_rate** (multi only) — the agent called `read_file`/`grep` on a path matching the
  scenario's `hidden_paths` glob *before* `final_answer`. The H4 axis, and the headline of the
  agentic track. Its validity check is **`verified_then_correct`** (success among verifiers) — reading
  the truth should rescue the answer.
- **output tokens** and **cost** — secondary. Input tokens differ by construction (the doc block's
  size), so only output tokens carry a behavioral signal.

### 3.7 Models, scale, and sampling

- **Models (5, across 3 providers).** Anthropic — `haiku` (`claude-haiku-4-5-20251001`), `sonnet`
  (`claude-sonnet-4-6`), `opus` (`claude-opus-4-8`); OpenAI — `gpt`; Google — `gemini`. Exact model
  ids and prices are pinned in `config.toml` at freeze time and copied into `run.json`.
- **Trials (tiered).** N = 10 per cell for the **cascade** family (the headline); N = 5 for the
  **comprehension** family (success-ceilinged — kept only for the token story). Comprehension may be
  omitted from multi mode entirely, since it does not test verification; that choice is recorded in
  `run.json`, not chosen by results.
- **Sampling.** `temperature = 1.0` (stochasticity is part of what we measure); `max_tokens = 1024`;
  `max_turns = 8` (multi mode).

### 3.8 Scenario validation and oracle tripwires

Two offline gates run before any spend, and one runs after every paid run:

- **`tools/author.py`** seals each scenario's documentation hub hashes against the real `surf` binary
  and emits the genuine `surf_report.json`. It **fails loudly** if the stale hub does not actually
  diverge — i.e., if the drift is not the kind `surf check` would catch.
- **`tools/validate_scenario.py`** runs the live graders on the two committed reference solutions and
  proves they **discriminate**: the correct solution scores `ok` and not `misled`; the stale solution
  scores `misled` and not `ok`. This certifies the grader's polarity offline.
- **`surface_bench.oracle`** is a post-run tripwire that exits non-zero if, per scenario × model,
  (a) C2-fresh success < 90% (with a *fresh* doc the task must be solvable; a low cell means the
  scenario is mis-authored, not a real effect), or (b) a cascade C1 *never* misleads (if a stale doc
  never produces the wrong answer, the drift is not load-bearing and the scenario measures nothing).

Spend is staged and gated: `mock` (offline pipeline check) → one scenario × each provider (smoke the
tool round-trip) → cascade-only multi at small N (pilot the verification metric) → the full matrix,
with the oracle as the gate at each step.

---

## 4. Pre-registration and analysis plan

The following was frozen before the confirmatory run (`PREREGISTRATION.md`). Direction is pre-specified
for **every** confirmatory hypothesis; anything not listed (per-provider contrasts, tier gradients,
token-cost deltas) is **exploratory** and reported as such.

### 4.1 Confirmatory hypotheses

| | Claim | Test | Read on |
|---|---|---|---|
| **H1** | accuracy beats rot (the core value) | success(C2) > success(C1) | success rate |
| **H2** | rot is worse than nothing (the headline) | misled(C1) > misled(C0) | misled rate |
| **H3** | surfacing drift recovers it | success(C3) ≈ success(C2), and ≫ C1 | success rate |
| **H4** | a confident stale doc suppresses verification | verification_rate(C1) < verification_rate(C0) | verification rate (multi) |
| **H5** | the harm flows through skipped verification (mediation) | within C1, success(verified) > success(not verified) | mediation (multi) |
| **H6** | recovery is the corrected code, not mere suspicion | success(C3) > success(Cw) | success rate |

### 4.2 Statistical analysis

- **Rates** are reported with 95% **Wilson** confidence intervals.
- **Each hypothesis** is tested as an unpaired difference of proportions with a 95% **bootstrap**
  confidence interval *and* a bootstrap two-sided p-value (10,000 resamples, fixed seed).
- **Multiplicity** is controlled with **Holm–Bonferroni** across the family of confirmatory
  success-delta tests (every model × pre-registered pair). A hypothesis is **confirmed** if its CI
  excludes 0 **and** it survives Holm; it is reported as **suggestive** if CI-significant but not
  Holm-significant.
- **H5 (mediation)** is reported as the within-C1 success split (verified vs not) per model.
- **Per-scenario and per-tier breakdowns** are reported for transparency (exploratory), so that no
  single broken fixture or single difficulty level can hide inside a family average.

### 4.3 Exclusions, stopping rule, and scope

- **Exclusions.** A cell that errors (API failure) is logged with `error` and **excluded** from
  rates; the count of excluded cells is reported. No silent retries beyond the client's built-in
  retry.
- **Fixture defects.** Any scenario failing the oracle (C2-fresh ≥ 90%, or cascade C1-misled > 0) is
  treated as a fixture defect and flagged; whether to drop it is decided by the pre-stated oracle
  rule, not by whether dropping it helps the result.
- **Stopping rule.** The matrix runs to completion at the fixed N above. No data-dependent stopping,
  no N top-ups chosen by looking at significance. If a *staging* smoke reveals a harness bug, it is
  fixed and that stage re-run; the confirmatory full run begins only after the pre-registration is
  tagged.
- **Scope.** The study assesses whether documentation accuracy changes single-shot and multi-turn
  task outcomes on curated cascade fixtures across five models, and whether the effect is mediated by
  verification. It does **not** assess real-repository generalization (curated fixtures by design),
  an edit/run/test agent loop (read-only by design), or languages beyond Python and TypeScript.

---

## 5. Preliminary results (single-shot pilot, 2026-06-13)

These are **real** results from the committed snapshot `results/2026-06-13-pilot-full-matrix/`. They
are **preliminary and motivating**, not confirmatory: this pilot ran the *secondary* (single-shot)
mode, four conditions (C0–C3; the **Cw** control and the multi-turn verification metrics were not yet
in the harness), and three Anthropic models. It therefore speaks to H1–H3 but **not** to H4, H5, or
H6.

**Configuration.** 11 scenarios (4 cascade, 7 comprehension) × 4 conditions × 3 models × N = 10 =
**1,320 graded completions, 0 errors**. `temperature = 1.0`, `max_tokens = 1024`, `surf 0.6.1`. Data
were assembled from an original run plus a resume after a timeout fix; every scenario has exactly 120
rows, 0 duplicates (see `PROVENANCE.md`).

### 5.1 Cascade family (hidden dependency) — n = 40 per condition per model

Success with 95% Wilson interval; "mis" = misled rate; "tok" = mean output tokens.

| Model | C0 (code only) | C1 (stale) | C2 (fresh) | C3 (stale + surf) |
|---|---|---|---|---|
| haiku | 2% [0–13] · mis 38% · 472 tok | **0% [0–9] · mis 100%** · 408 | **100% [91–100]** · 0% · 427 | **90% [77–96]** · 0% · 583 |
| sonnet | 0% [0–9] · mis 62% · 628 | **0% [0–9] · mis 100%** · 274 | **100% [91–100]** · 0% · 273 | **100% [91–100]** · 0% · 492 |
| opus | 0% [0–9] · mis 18% · 716 | **0% [0–9] · mis 100%** · 398 | **100% [91–100]** · 0% · 419 | **100% [91–100]** · 0% · 634 |

Success deltas: **H1 (C2 − C1) = +100 pp on every model**; **H3 (C3 − C1) = +90 pp (haiku), +100 pp
(sonnet, opus)**.

### 5.2 Comprehension family (visible code) — n = 70 per condition per model

| Model | C0 (code only) | C1 (stale) | C2 (fresh) | C3 (stale + surf) |
|---|---|---|---|---|
| haiku | 86% [76–92] · mis 13% · 425 | 86% [76–92] · mis 10% · 496 | 100% [95–100] · 0% · 431 | 96% [88–99] · 0% · 489 |
| sonnet | 93% [84–97] · 0% · 434 | 99% [92–100] · 0% · 479 | 100% [95–100] · 0% · 372 | 100% [95–100] · 0% · 426 |
| opus | 100% [95–100] · 0% · 403 | 94% [86–98] · 0% · 472 | 99% [92–100] · 0% · 415 | 96% [88–99] · 0% · 463 |

Success ceilings near 100% across the board — the model can just read the visible code. The signal
here is **tokens**: a stale doc costs **+65 (haiku), +107 (sonnet), +57 (opus)** extra output tokens
versus a fresh doc (C1 − C2).

### 5.3 Spend

| Model | Spend |
|---|---|
| haiku | $1.49 |
| sonnet | $4.21 |
| opus | $8.28 |
| **Total** | **$13.98** |

### 5.4 What the pilot establishes (and does not)

- **Establishes (preliminary):** when the dependency is hidden, a stale doc drives cascade success to
  **0%** and misled rate to **100%** on every model, with **fresh docs at 100%** and the **surf report
  recovering to 90–100%** — and crucially, **capability does not help** (haiku, sonnet, and opus
  collapse identically). Where code is visible, rot does not break correctness but levies a token tax.
- **Does not establish:** anything about verification behavior (H4/H5), the warning-only control
  (H6/Cw), the multi-turn setting where the agent *could* verify, or generalization beyond Anthropic.
  Those are precisely what the confirmatory study (§6) adds.

---

## 6. Headline results — multi-turn agentic study `[RESULTS PENDING]`

> This section is reserved for the confirmatory run. The tables and decision lines below are the
> skeleton to be filled directly from `summary.json` once the matrix completes; **no figures are
> entered until then.** Statistics follow §4 (Wilson rates, bootstrap delta CIs + p-values,
> Holm–Bonferroni across the confirmatory family).

### 6.1 Run provenance `[RESULTS PENDING]`

Pre-registration tag, `surf --version`, model ids/prices, conditions, scenarios, N, max_turns, total
calls, excluded (errored) cells, total spend.

### 6.2 Success and misled rates — per model × condition (cascade) `[RESULTS PENDING]`

| Model | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| haiku | … | … | … | … | … |
| sonnet | … | … | … | … | … |
| opus | … | … | … | … | … |
| gpt | … | … | … | … | … |
| gemini | … | … | … | … | … |

(success [Wilson CI] · misled · output tokens, per cell.)

### 6.3 Verification rate — per model × condition (cascade, multi only) `[HEADLINE PENDING]`

| Model | C0 | C1 | C2 | C3 | Cw | `verified_then_correct` |
|---|---|---|---|---|---|---|
| … | … | … | … | … | … | … |

H4 deltas (verification_rate(C0) − verification_rate(C1)) with bootstrap CI + Holm flag per model.

### 6.4 Mediation (H5) — within-C1 success split `[RESULTS PENDING]`

Per model: success among rows that verified the hidden dependency vs success among rows that did not.

### 6.5 Confirmatory decisions `[RESULTS PENDING]`

Complete each with **confirmed / suggestive / not supported** plus the delta, bootstrap CI, p-value,
and Holm outcome:

- **H1** success(C2) > success(C1): `[PENDING]`
- **H2** misled(C1) > misled(C0): `[PENDING]`
- **H3** success(C3) ≈ success(C2) ≫ C1: `[PENDING]`
- **H4** verification_rate(C1) < verification_rate(C0): `[PENDING]`
- **H5** within C1, success(verified) > success(not verified): `[PENDING]`
- **H6** success(C3) > success(Cw): `[PENDING]`

### 6.6 Cross-provider generalization (exploratory) `[RESULTS PENDING]`

Per-provider deltas for the key contrasts, addressing whether "capability does not buy
rot-resistance" holds across Anthropic, OpenAI, and Google.

### 6.7 Token cost (exploratory) `[RESULTS PENDING]`

Output-token deltas (C1 − C2, C1 − C0, C1 − C3) per model and family.

---

## 7. Discussion

The interpretive scaffolding below is stated to the extent the design and preliminary data already
support it; claims that depend on the confirmatory run are marked.

### 7.1 You cannot out-model a stale doc about code you can't see

The pilot's strongest signal is the flat **+100 pp** H1 effect across the capability range: when the
drifted dependency is hidden, haiku, sonnet, and opus are *all* 0% correct and 100% misled under a
stale doc. This is the central refutation of "just use a better model." A more capable model reasons
more fluently about the wrong premise; it does not spontaneously distrust a confident, plausible doc
about a file it cannot see. **Whether a stronger model in a multi-turn setting compensates by
verifying more often is exactly H4, and is `[HEADLINE PENDING]`.**

### 7.2 Two distinct costs of rot

The pilot exposes two failure economics:

- **Rot you can't see makes you wrong.** In the cascade family, a confident stale doc makes the model
  *cheaply* wrong — C1 spends *fewer* output tokens than C0 (e.g., sonnet 274 vs 628), because with no
  doc the model deliberates about the unseen dependency, whereas a stale doc lets it commit to the
  wrong answer immediately. The expense reappears in **recovery**: C3 is the costliest condition.
- **Rot you can see makes you slow.** In the comprehension family, where the model gets the answer
  right anyway by re-reading code, the cost is a steady **token tax** (+57–107 tokens) for reconciling
  stale prose against visible code.

In one line: **rot you can't see makes you wrong; rot you can see makes you slow.**

### 7.3 The mechanism (the non-tautological core)

The single-shot result is open to the objection that, with the dependency hidden, following the doc is
the only available move. The multi-turn track answers this by giving the agent the *option* to verify.
If H4 holds — a confident stale doc lowers verification rate relative to no doc — then the harm is not
about availability of information but about the doc *suppressing the agent's own checking*. H5 closes
the loop: within C1, verifiers should be correct and non-verifiers misled, making verification the
mediator of the effect. **Both are `[HEADLINE PENDING]`.**

### 7.4 Is it the fix, or just suspicion? (C3 vs Cw)

C3 hands the agent Surface's corrected code; Cw hands it only a content-free "may be outdated"
warning. H6 (C3 > Cw) is what separates "surfacing the *fix* recovers performance" from "merely making
the agent suspicious recovers performance." A null H6 would be an important, publishable negative
result — it would suggest much of the value is in distrust, not in the specific correction.
`[RESULTS PENDING]`.

### 7.5 Cost impact for decision-makers

Two cost questions matter: how much does rot add to *model spend* (measured here), and how much does
it cost in *wrong work* (measured as a rate; priced with the reader's own numbers).

**Token spend — measured, and small.** Where the model can see the code, keeping docs fresh trims the
wasted generation a stale doc provokes. Priced at the pilot's rates: ≈ **$0.31** (haiku), **$1.56**
(sonnet), **$1.29** (opus) per 1,000 tasks. This is a *floor*: single-shot tasks have no multi-turn
thrash; a tool-using agent that loops on a misleading doc would waste more.

**Avoided wrong work — the dominant term.** The real cost of rot is the wrong change the model ships
when it cannot verify a stale doc. The pilot result is stark: **without Surface, a wrong result on
100% of tasks that relied on a drifted, unseen dependency; with Surface (fresh docs, or the drift
report), roughly 0%.** A back-of-envelope model:

> monthly saving ≈ (agent tasks / month) × (share relying on drifted, unverifiable docs) ×
> (failure-rate drop, ≈100% → ~0%) × (cost to remediate one wrong change)

Illustrative (substitute your own numbers): 10,000 tasks/month × 2% exposure × (100% → ~0%) × $50 to
catch-and-fix one wrong change ≈ **$10,000/month** in avoided rework — against a few dollars on the
token line. **The ROI is dominated by avoided wrong work, not token savings**, and it scales with how
often agents act on documentation they cannot independently verify. *Measured here:* the 100%/≈0%
failure rates and the token deltas. *Supplied by the reader:* task volume, exposure share, and
remediation cost.

---

## 8. Threats to validity

### 8.1 Internal validity (mitigated by design)

- **Doc-trust bias from prompting.** A persona or a "code is ground truth" instruction would bias the
  agent toward (or away from) the doc. *Mitigation:* a minimal, persona-free system prompt with no
  declared precedence (§3.5).
- **Value leakage.** If the stale or fresh value appears in the task text, a worked example, or the
  visible code, the manipulation is contaminated. *Mitigation:* the stale value appears only in the
  stale hub; `task.md` is neutral. This bit the first pilot (issue #113) and is now an authoring rule
  with a checklist.
- **Non-load-bearing drift.** A drift where T0 and T1 produce the same output measures nothing.
  *Mitigation:* authors must name an input where T0 and T1 differ; the oracle flags any cascade C1
  that never misleads.
- **Grader polarity / hardcoded truth.** *Mitigation:* `validate_scenario.py` proves offline that the
  correct and stale reference solutions are discriminated; cascade graders probe the *real* hidden
  dependency rather than hardcoding the fresh value.
- **Non-determinism.** *Mitigation:* graders contain no clocks, network, or randomness in the checked
  logic; fixed probe inputs; **no LLM judge**.
- **Guess resistance.** Single-shot cascade is guess-resistant only because the hidden value is
  genuinely unknowable without the doc (a stated limitation that the multi-turn track removes); QA
  verdicts use two fields to cut a 50/50 guess.
- **Infrastructure failures.** *Mitigation:* per-request timeout + bounded retries; errored cells
  excluded and counted, not scored as failures.

### 8.2 External validity (disclosed limitations)

- **Curated fixtures, not real repositories.** All scenarios are bespoke; external validity is
  limited. A real-OSS case study is deferred future work.
- **Read-only agent loop.** No edit/run/test "thrash"; the compounding cost of rot is not measured.
- **Language coverage.** Python and TypeScript only.
- **Single-anchor scenarios.** The sealing tool currently seals only the first anchor per hub, so no
  genuine multi-claim scenarios yet.
- **Contamination (residual).** Frontier models may have seen similar idioms (boundary checks,
  retries, page sizes) in training. The drift *values* live only in the stale hub and the fixtures are
  not scraped, but the residual risk is acknowledged rather than eliminated.
- **In-context drift only (upstream scope).** We study a doc that is *already* in context and has
  drifted from its code; we do not model the retrieval stage that selects which docs reach the agent.
  Retrieval-side defenses (temporal filtering, metadata boosting; Murúa, 2026) are complementary but
  out of scope — and, as noted in §2.4, recency filtering does not catch a recently-edited doc whose
  code has since moved, which is exactly the drift we measure.

---

## 9. Ethics and disclosures

- **No human subjects.** All data are model completions on synthetic, author-written fixtures.
- **Competing interest, declared.** The author of this benchmark also authors the Surface tool whose
  value it measures. The study is pre-registered, the grading is deterministic and inspectable, the
  raw per-call data are released, and a negative result on any hypothesis (notably H6) is reportable —
  design choices intended to make the conflict non-determinative of the conclusions.
- **Vendor neutrality.** The harness is provider-agnostic; models from three vendors run the identical
  scenario suite under identical grading, and the agent loop and graders never learn which provider
  produced an output.

---

## 10. Reproducibility and data availability

- **Environment.** The Python harness is pinned by `uv.lock`; code-edit graders run under the same
  interpreter `uv run` selects.
- **Provenance.** `run.json` records every parameter (model ids and prices, trials, temperature,
  max_tokens, mode, max_turns, conditions, scenarios, `surf --version`).
- **Re-gradeable data.** `raw.jsonl` preserves raw model outputs, so grading and metrics can be re-run
  offline without re-spending; `report` regenerates `summary.json`, `report.md`, and figures from a
  frozen `raw.jsonl`.
- **Reproducing the pilot snapshot:**
  ```sh
  uv sync
  export ANTHROPIC_API_KEY=...
  uv run python -m surface_bench.run --models haiku sonnet opus --mode single --trials 10
  uv run python -m surface_bench.report results/<timestamp>
  uv run python -m surface_bench.oracle results/<timestamp>
  ```
- **Artifacts.** Harness, scenarios, graders, reference solutions, the pre-registration, the ABC
  self-audit, and the committed pilot snapshot are all in the `surface-bench` repository.

---

## 11. Conclusion

Documentation rot is usually treated as a hygiene problem. For autonomous coding agents it is a
*correctness* problem: when the code that actually implements a behavior is out of view, a confident
but stale doc is the agent's only window onto a world that has moved, and the agent acts on a fact that
is no longer true. Our single-shot pilot shows this failure is total and capability-invariant — every
model wrong on every hidden-dependency task under a stale doc — and that accurate docs, or simply
surfacing the drift, restore correctness. The confirmatory multi-turn study asks the deeper question:
not merely whether stale docs *can* mislead an agent that has no alternative, but whether a confident
stale doc *suppresses* an agent's own verification when verification is freely available.
`[HEADLINE PENDING]`

---

## References

- Y. Zhu et al. *Establishing Best Practices for Building Rigorous Agentic Benchmarks.* NeurIPS 2025
  Datasets & Benchmarks Track. arXiv:2507.02825.
- T. Murúa. *How to defend your RAG system from context poisoning.* Elastic Search Labs, 10 Feb 2026.
  https://www.elastic.co/search-labs/blog/context-poisoning-llm (industry / grey literature).
- Surface — documentation-drift gate. https://github.com/Connorrmcd6/surface
- surface-bench — this benchmark and its pre-registration, ABC self-audit, and pilot snapshot.
  https://github.com/Connorrmcd6/surface-bench

---

*Companion documents in this repository: `PREREGISTRATION.md` (frozen hypotheses + analysis plan),
`ABC_CHECKLIST.md` (benchmark-rigor self-audit), `README.md` (operator manual), and
`results/2026-06-13-pilot-full-matrix/report.md` (the standalone pilot write-up).*

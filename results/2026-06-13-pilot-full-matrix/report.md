# Surface agent-impact benchmark — pilot report (2026-06-13)

A standalone write-up of the first full pilot: what we ran, why, how, what we observed, and what we
learned. Machine-readable metrics are in `summary.json`; the raw per-call data is in `raw.jsonl`;
per-model success plots are `success_{haiku,sonnet,opus}.png`. Run provenance is in `PROVENANCE.md`.

---

## 1. Overview

**Question.** Surface is a documentation-drift gate: it doesn't make an agent smarter, it stops
docs silently rotting. So its value to an agent should equal the *performance gap between working
from accurate docs and from rotted docs*. This benchmark measures that gap directly, using drift of
exactly the kind `surf check` catches (a flipped operator, a changed constant, an inverted
condition, a dropped guard).

**Design in one line.** Same code, same task, same model in every run — **only the documentation
block changes** — across four conditions, and we measure how the agent's success, error mode, and
token cost move.

**Top-line result.** When the drifted code is *hidden* from the agent (it knows the dependency only
by its doc — the realistic case in a large codebase), a stale doc makes **every model wrong 100% of
the time**, and **a more capable model is no more resistant** (haiku, sonnet, and opus all collapse
identically). Accurate docs restore 100% success, and handing the agent Surface's drift report
recovers nearly all of the loss. When the code is *visible*, rot doesn't break correctness but
imposes a consistent **token tax**.

---

## 2. Hypotheses

Let C0 = code only, C1 = code + stale doc, C2 = code + fresh doc, C3 = code + stale doc + `surf
check` report.

- **H1 — accuracy beats rot (the core value):** C2 > C1.
- **H2 — rot is worse than nothing (the headline):** C1 < C0.
- **H3 — surfacing drift recovers the loss:** C3 ≈ C2.

A secondary metric, **misled rate**, tracks whether the agent asserted the *stale* claim (parroted
the rotted doc) rather than merely failing.

---

## 3. Methodology

### 3.1 Conditions

Every run is identical except the documentation block in the prompt:

| Condition | Context shown to the agent | Represents |
|---|---|---|
| **C0** | code only | baseline |
| **C1** | code + **stale** doc (true at T0, code moved to T1) | the ungoverned world |
| **C2** | code + **fresh** doc (matches T1) | the Surface-governed world |
| **C3** | code + stale doc + real `surf check --format json` report | "just surface the drift" |

Each scenario has a *drifted* current state (T1) and a pre-drift state (T0). The stale doc
truthfully described T0; the code has since moved to T1. The hub anchors are sealed by the real
`surf` binary via `tools/author.py`, so the C3 report is genuine `surf check` output, not a mock.

### 3.2 Two scenario families

- **Comprehension** (7 scenarios): the drifted code **and** its contradicting doc are both in the
  prompt. Tests whether an agent re-derives truth from code it can see.
- **Cascade** (4 scenarios): the realistic context-rot shape. The agent edits a *visible* function
  whose correctness depends on a **hidden dependency** — the drifted code is withheld from the
  prompt (listed in `meta.toml`'s `hidden_paths`), so the agent knows it *only* through its doc.
  The dependency's real source stays in the workspace so `surf` can seal a real divergence and the
  grader can run the agent's edit against reality. The grader derives the expected value from the
  real hidden dependency, so the test stays honest.

### 3.3 Models, sampling, scale

- Models: **haiku** (`claude-haiku-4-5-20251001`), **sonnet** (`claude-sonnet-4-6`), **opus**
  (`claude-opus-4-8`).
- **N = 10** completions per (scenario × condition × model); temperature 1.0 (stochasticity is part
  of what we measure); max 1024 output tokens.
- Total: 11 scenarios × 4 conditions × 3 models × 10 = **1320 calls**.

### 3.4 Grading (deterministic, no LLM judge)

- **QA scenarios:** the agent ends with a fixed-format `VERDICT:` line; a rubric parses the fields
  and adjudicates `correct` (matches T1) vs `misled` (matches the stale T0 claim).
- **Code-edit scenarios:** the agent returns full files in `FILE:` blocks; we overlay them onto the
  workspace and run hidden tests — a `correct` check (T1 behaviour) and a `misled` check (T0
  behaviour). Cascade graders derive the expected value from the real hidden dependency.

Three metrics per cell: **success rate**, **misled rate**, and **output-token cost** (input tokens
differ by construction — the doc block's size — so only output tokens are a behavioural signal).
Rates carry 95% Wilson intervals; deltas use a 95% bootstrap CI.

### 3.5 The 11 scenarios

**Cascade (hidden dependency):**

| Scenario | Lang | Hidden dependency drift |
|---|---|---|
| `cascade-quota-batcher-code` | py | limiter capacity, `<` → `<=` (admits N+1) |
| `cascade-retry-budget-code` | py | retry attempt cap, 3 → 5 |
| `cascade-access-policy-code` | py | allow-list → block-list inversion |
| `cascade-page-size-ts-code` | ts | default page size, 50 → 25 |

**Comprehension (visible code):** `refresh-single-use-qa`, `refresh-replay-premise-qa`,
`access-invert-qa`, `dropped-await-qa` (QA); `ratelimit-window-code`, `retry-budget-code`,
`pagination-ts-code` (code-edit).

---

## 4. Prompts given to the agents

The prompt is `(system, user)`. Only the **documentation block** in the user turn changes across
conditions; the system prompt, code, and task are byte-identical.

### 4.1 System prompt

```
Use the files and documentation provided to do the task below.
```

Deliberately minimal and **persona-free** — no "you are an expert engineer" framing (which primes
diligent, skeptical behaviour and biases against a stale-doc effect) and **no precedence** declared
between docs and code. This mirrors how people actually prompt: paste/tag some files, maybe a doc,
ask for the change.

### 4.2 User-turn structure

````
## Codebase
### <path>
```<lang>
<file contents>      ← cascade scenarios omit the hidden dependency here
```
...

## Project documentation          ← omitted entirely in C0
The repository documents this area as follows:
<hub: a YAML-fronted doc whose anchored claim is the stale (C1) or fresh (C2) contract>

## Automated documentation check  ← C3 only
Surface (a deterministic doc-drift gate) reports that the anchored claim above no longer
matches the code it points at ...
```json
<genuine `surf check --format json` output, including the corrected `new_code`>
```

## Task
<the task: QA question ending in a VERDICT line, or a code-edit asking for full FILE: blocks>
````

### 4.3 Worked example — `cascade-quota-batcher-code`

The agent sees `throttle.py` and is asked to implement `plan_batches(total)`, which must size
batches to the limiter's per-window capacity. **The limiter's source is hidden**, so the capacity
is knowable only from the doc. The drift: the limiter's admission test moved `<` → `<=`, so its true
capacity for `WINDOW_LIMIT = 10` is **11**, not 10.

- **C1 (stale doc)** asserts: *"a limiter built with limit=N has a per-window capacity of exactly N
  … at WINDOW_LIMIT = 10 the limiter admits 10."* → an agent that trusts it batches at 10 (wrong).
- **C2 (fresh doc)** asserts: *"inclusive bound (count <= limit) … admits N+1 … at WINDOW_LIMIT = 10
  the limiter admits 11."* → batches at 11 (correct).
- **C3** keeps the stale prose but appends the `surf` report, whose `new_code` shows
  `if count <= self.limit:` — the only window onto the truth when the file is hidden.

Approximate prompt sizes for this scenario: C0 ~1.96k chars, C1/C2 ~3.29k, C3 ~5.04k.

---

## 5. Results

N = 10 per cell. Success shown with 95% Wilson interval; "mis" = misled rate; "tok" = mean output
tokens.

### 5.1 Cascade family (hidden dependency) — n = 40 per condition per model

| Model | C0 (code only) | C1 (stale) | C2 (fresh) | C3 (stale + surf) |
|---|---|---|---|---|
| haiku | 2% [0–13] · mis 38% · 472 tok | **0% [0–9] · mis 100%** · 408 | **100% [91–100]** · 0% · 427 | **90% [77–96]** · 0% · 583 |
| sonnet | 0% [0–9] · mis 62% · 628 | **0% [0–9] · mis 100%** · 274 | **100% [91–100]** · 0% · 273 | **100% [91–100]** · 0% · 492 |
| opus | 0% [0–9] · mis 18% · 716 | **0% [0–9] · mis 100%** · 398 | **100% [91–100]** · 0% · 419 | **100% [91–100]** · 0% · 634 |

Deltas (success): **H1 (C2−C1) = +100pp on every model**; **H3 (C3−C1) = +90pp (haiku), +100pp
(sonnet, opus)**.

### 5.2 Comprehension family (visible code) — n = 70 per condition per model

| Model | C0 (code only) | C1 (stale) | C2 (fresh) | C3 (stale + surf) |
|---|---|---|---|---|
| haiku | 86% [76–92] · mis 13% · 425 | 86% [76–92] · mis 10% · 496 | 100% [95–100] · 0% · 431 | 96% [88–99] · 0% · 489 |
| sonnet | 93% [84–97] · 0% · 434 | 99% [92–100] · 0% · 479 | 100% [95–100] · 0% · 372 | 100% [95–100] · 0% · 426 |
| opus | 100% [95–100] · 0% · 403 | 94% [86–98] · 0% · 472 | 99% [92–100] · 0% · 415 | 96% [88–99] · 0% · 463 |

Success ceilings near 100% across the board (the model can just read the visible code). The signal
here is **tokens**: a stale doc costs **+65 (haiku), +107 (sonnet), +57 (opus)** extra output tokens
vs a fresh doc (C1 − C2).

### 5.3 Spend

| Model | Spend |
|---|---|
| haiku | $1.49 |
| sonnet | $4.21 |
| opus | $8.28 |
| **Total** | **$13.98** |

1320 calls, 0 errors.

---

## 6. Interpretation

**1. When the dependency is hidden, a stale doc breaks every model — and capability doesn't save
you.** Cascade C1 is 0% success / 100% misled on haiku, sonnet, *and* opus. H1 = +100pp flat across
the capability range. You cannot out-model a stale doc about code you can't see. This is the
headline and the strongest refutation of "just use a better model."

**2. Accurate docs and the surf report both fix it.** C2 = 100% everywhere (H1). C3 recovers to
100% on sonnet/opus and 90% on haiku (H3) — the report's embedded `new_code` is enough to rescue the
agent even though the file is hidden. Surfacing drift works.

**3. H2 lives in the *misled* axis, not just success.** With no doc (C0) the models guess and land
on the stale value only sometimes (38% haiku, 62% sonnet, 18% opus); with the stale doc (C1) they
are misled **100%** of the time. The rotted doc doesn't just fail to help — it reliably *causes* the
wrong answer.

**4. Two different costs of rot.** In the cascade family a confident stale doc makes the model
*cheaply wrong*: C1 spends **fewer** output tokens than C0 (e.g. sonnet 274 vs 628), because with no
doc the model deliberates about the unseen dependency, while a stale doc lets it commit to the wrong
answer immediately. The expense reappears in **recovery** — C3 is the costliest condition. In the
comprehension family, where the model gets the answer right anyway, the cost is a steady **token
tax** (+57–107 tokens) for reconciling stale prose against visible code.

In short: **rot you can't see makes you wrong; rot you can see makes you slow.**

---

## 7. Cost impact for decision-makers

Two cost questions matter: *how much does rot add to model spend?* (measured here) and *how much
does rot cost in wrong work?* (measured as a rate; priced with your own numbers).

### 7.1 Token spend — measured, and small

Where the model can see the code, keeping docs fresh (the Surface-governed world, C2) trims the
wasted generation that a stale doc (C1) provokes. Priced at this run's rates:

| Model | Wasted model spend from stale docs (C1 − C2) |
|---|---|
| haiku | ≈ $0.31 per 1,000 tasks |
| sonnet | ≈ $1.56 per 1,000 tasks |
| opus | ≈ $1.29 per 1,000 tasks |

Real but minor — and a **floor**: these are single-shot tasks, so there is no multi-turn "thrash"; a
tool-using agent that loops on a misleading doc would waste far more. Note that where the code is
*hidden*, a stale doc actually spends slightly *fewer* tokens (being confidently wrong is cheap), so
token accounting alone **understates** Surface's value — the value there is correctness, next.

### 7.2 Avoided wrong work — the dominant term

The real cost of rot is not tokens; it is the wrong change the model ships when it cannot verify a
stale doc. There the result is stark: **without Surface the model produced a wrong result on 100% of
tasks that relied on a drifted, unseen dependency; with Surface (fresh docs, or the drift report)
roughly 0%.** Price one wrong change — caught and fixed in review, or worse, shipped — and the
saving follows directly:

> **monthly saving ≈ (agent tasks / month) × (share that rely on drifted, unverifiable docs) ×
> (failure-rate drop, ≈100%→0%) × (cost to remediate one wrong change)**

Illustrative — substitute your own numbers:

| Input | Example |
|---|---|
| Agent tasks / month | 10,000 |
| Share touching a drifted, unseen dependency | 2% (1 in 50) |
| Failure-rate reduction with Surface | 100% → ~0% |
| Cost to catch & fix one wrong change | $50 (≈30 min eng @ $100/hr) |
| **Estimated avoided rework** | **≈ $10,000 / month** |

On those same 10,000 tasks the token line is a few dollars. The takeaway for a decision-maker:
**Surface's ROI is dominated by avoided wrong work, not token savings**, and it scales with how often
your agents act on documentation they cannot independently verify.

*Measured here:* the 100%/≈0% failure rates and the token deltas. *Supplied by you:* task volume,
exposure share, and remediation cost — the bracketed example is an illustration, not a claim about
your environment.

---

## 8. Learnings

- **The framing decides the result.** Our first attempt used only comprehension scenarios and a
  system prompt that said *"the source code is the ground truth."* haiku hit a 100%-success / 0%-
  misled ceiling — we were measuring "do stale docs mislead agents?" while instructing the agent
  not to be misled. (Recorded in issue #113.) Fixes: neutralize the prompt, and model the realistic
  cascade where the drifted dependency is hidden.
- **Hidden-dependency is what makes the doc load-bearing.** Once the agent can't see the drifted
  code, the doc is its only source of truth, and rot has somewhere to bite. This single change moved
  the cascade family from "measures nothing" to a clean +100pp effect.
- **The harness is sensitive enough to catch authoring mistakes.** An early cascade run showed C3
  failing to recover; inspecting the transcripts revealed the model was obeying a phrase in *our own
  task text* ("work from its documentation") and an example in the visible file that anchored the
  stale value. Removing both restored recovery. Lesson: author cascades neutrally and never leak the
  stale value through wording or worked examples.
- **Comprehension scenarios ceiling on correctness but still pay the token tax.** They are weak for
  the success story and useful for the cost story — keep them, but read them on tokens.
- **Robustness bug found in flight.** The original matrix run hung on a single API request that
  never returned — the client had no wall-clock timeout, so one bad request stalled the whole
  matrix. Fixed by adding a 120s per-request timeout + retries; completed rows were preserved and
  the unfinished scenarios re-run (see `PROVENANCE.md`).

---

## 9. Future work

- **Multi-turn / tool-using agent.** This pilot is single-shot. A real agent loop (read files, run
  tests, iterate) would let us measure the *thrash* cost of rot directly and is likely where the
  wasted-token signal is largest.
- **Other providers.** The model layer is provider-agnostic; add OpenAI / Gemini / etc. adapters to
  test whether the "capability doesn't buy rot-resistance" finding generalizes beyond Claude.
- **A real-OSS case study.** Take an actual repository, introduce a realistic drift, and reproduce
  the cascade effect outside curated fixtures — the strongest external-validity evidence.
- **Larger N and harder comprehension scenarios.** Tighten CIs; redesign the ceilinged comprehension
  scenarios so the truth is costlier to re-derive, giving them a correctness gradient too.
- **Report the gradient by re-derivation cost.** The current tier axis hints that the Surface effect
  grows as recovering truth from code gets more expensive; a cleaner difficulty ladder would make
  that explicit.

---

## 10. Reproducibility

- Data assembled from two runs at the same prompts/grading (an original run + a resume after the
  timeout fix); every scenario has exactly 120 rows, 0 duplicates, 0 errors. See `PROVENANCE.md`.
- Re-run the pipeline from the repo root:
  ```sh
  cargo build --release
  cd bench && uv sync
  export ANTHROPIC_API_KEY=...
  uv run python -m surface_bench.run --models haiku sonnet opus --trials 10
  uv run python -m surface_bench.report results/<timestamp>
  ```
- Note: re-running `surface_bench.report` regenerates the auto-generated tables; this file is an
  authored report for the committed snapshot. `summary.json` holds the machine-readable metrics.

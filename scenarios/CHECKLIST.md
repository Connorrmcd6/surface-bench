# Authoring a cascade scenario

A *cascade* scenario: the agent edits a **visible** file whose correctness depends on a **hidden**
dependency (in `code/`, listed in `meta.toml` `hidden_paths`, filtered out of the prompt). The
dependency has drifted from what the **stale** doc says, so an agent that trusts the stale doc is
wrong. The graders probe the *real* hidden dependency for ground truth. Clone
`cascade-quota-batcher-code/` as the canonical template.

## 0. Pick a load-bearing drift
- [ ] Choose a drift archetype **not already in the family** (avoid: boundary `<`→`<=`, plain
      constant, allow→block, page-size constant — see existing `cascade-*`).
- [ ] Name a concrete input where **T0 and T1 produce different observable outputs**. If you can't,
      the drift isn't load-bearing — stop and rethink. (The whole effect dies if T0 ≈ T1.)

## 1. Directory skeleton  (`scenarios/<id>/`)
- [ ] `meta.toml`: `id`, `title`, `lang`, `task_type`, `tier`, `anchor = "code/<file> > Symbol >
      method"`, `invariant`, `drift`, `hidden_paths` (glob over the dependency), `edit_path` (the
      visible file the agent returns — code scenarios only).
- [ ] `code/` — the **T1 (drifted)** source. Hidden dependency present; the visible file is a
      **stub** (`raise NotImplementedError` / TODO). No leaked value anywhere in `code/`.
- [ ] `.author/code_t0/` — **only the files that changed**, in their pre-drift (T0) form.
- [ ] `hub_stale.md` — TOML front matter (`summary`, `anchors:` with `claim`/`at`/`hash`, `refs`) +
      prose, describing **T0**. Use a placeholder `hash: 000000000000` (author.py seals it).
- [ ] `hub_fresh.md` — same `anchor`, describing **T1**. Placeholder hash.
- [ ] `task.md` — neutral (see §3). For code, ends with the exact `FILE: <edit_path>` contract.
- [ ] Grader —
      - code: `grader/grader.toml` (`setup_files=["tests"]`, `correct_cmd`, `misled_cmd`) +
        `grader/tests/check_correct.*` + `check_misled.*`.
      - qa: `grader/rubric.toml` (`type="verdict"`, `[fields.<x>]` regex, `[correct]`, `[misled]`).
- [ ] `.author/solution_correct.<ext>` and `.author/solution_stale.<ext>` — reference solutions for
      the polarization self-test (code: the visible file's body; qa: a `.txt` ending in the VERDICT).

## 2. Grader rules
- [ ] `check_correct` **derives ground truth by importing/probing the real hidden dependency** — never
      hardcode the T1 value. `check_misled` hardcodes the **stale** doc value and asserts the agent
      used it. (See `cascade-quota-batcher-code`'s `true_capacity()` probe.)
- [ ] Both exit non-zero on a failed assertion (`assert` / `raise SystemExit`).
- [ ] Choose a probe input where stale vs correct give **different** results (e.g. 25 → `[10,10,5]`
      stale vs `[11,11,3]` correct).

## 3. Neutrality (the #113 lesson — leaks killed the effect once)
- [ ] `task.md` states the goal + output contract only. **No worked example that reveals the stale or
      the fresh value** (an illustrative example with an *unrelated* placeholder number is fine).
- [ ] No "the doc may be wrong" hint, no precedence between doc and code.
- [ ] The stale value appears **only** in `hub_stale.md` — never in `task.md` or the visible code.

## 4. Seal + validate (offline, no spend)
- [ ] `python tools/author.py scenarios/<id>` — seals hub hashes, emits `surf_report.json`, asserts a
      `"changed"` divergence (fails loudly if the drift isn't detectable).
- [ ] `python tools/validate_scenario.py scenarios/<id>` — proves the graders discriminate
      (`solution_correct` → ok & not misled; `solution_stale` → not ok & misled).

## 5. Pipeline smoke
- [ ] `python -m surface_bench.run --models mock --scenarios <id>` — runs end to end, no API cost.
- [ ] `python -m surface_bench.oracle results/<ts>` — tripwires clear.

## Language notes
- python / typescript runtimes are always available (python3 via `sys.executable`; `node --test`,
  TS type-stripped on Node ≥ 22.18). Scenarios are Python + TS only.

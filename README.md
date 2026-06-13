# surface-bench

Empirically measuring how much **documentation accuracy** changes an agent's task performance —
the gap [Surface](../README.md) exists to protect.

Surface doesn't make an agent smarter; it stops docs silently rotting. So its value to an agent
equals the performance delta between working from **fresh** docs and **rotted** docs. This bench
measures that delta directly, using drift of exactly the kind `surf check` catches (flipped
operators, dropped guards, changed constants).

This lives in the Surface repo for now but has no inbound dependency on the Rust core — it only
*consumes* the `surf` binary's output — so it can be extracted to a standalone repo later.

## The experiment

Same code + same task in every run; **only the documentation block changes**:

| | Context shown to the agent | Represents |
|---|---|---|
| **C0** | code only | baseline |
| **C1** | code + **stale** doc (true at T0, code moved to T1) | the ungoverned world |
| **C2** | code + **fresh** doc (matches T1) | the Surface-governed world |
| **C3** | code + stale doc + real `surf check --format json` report | "just surface the drift" |

Hypotheses: **H1** C2 > C1 (accuracy beats rot — the core value) · **H2** C1 < C0 (rotted docs are
*worse than nothing*) · **H3** C3 ≈ C2 (surfacing drift recovers the loss).

Three metrics per condition: **success rate** (deterministic grader), **misled rate** (the agent
asserted the stale claim), and **output-token cost** (does a stale doc cost extra generation to
course-correct?).

Every run also reports **estimated spend** (`Total: $X`) — token usage × the per-model
`input_per_mtok` / `output_per_mtok` prices in `config.toml`. The report's per-call estimate is for
relative comparison; your Anthropic console invoice is the authoritative total for the "I spent $X
validating Surface" figure.

## Layout

```
bench/
  config.toml              models, trials, temperature
  surface_bench/           models · prompts · run · grade_qa · grade_code · metrics · report
  scenarios/<id>/          meta.toml · code/ · hub_stale.md · hub_fresh.md · surf_report.json · task.md · grader/
  tools/author.py          regenerate a scenario's hashes + surf_report.json with the real surf binary
  results/<timestamp>/     raw.jsonl · run.json · summary.json · report.md (gitignored)
```

## Run it

The harness env is managed with [uv](https://docs.astral.sh/uv/) (the committed `uv.lock` pins it
so the "I spent $X validating Surface" figure is reproducible). `uv run` puts the project venv's
interpreter first, and the code-edit graders execute under that *same* interpreter — so there is no
`python3`-on-PATH guessing.

```sh
cargo build --release                      # from repo root: provides target/release/surf
cd bench && uv sync                         # add --extra plots for charts, --extra dev for pytest

# offline pipeline check — no API key, no tokens
uv run python -m surface_bench.run --models mock

# real pilot
export ANTHROPIC_API_KEY=...
uv run python -m surface_bench.run --models haiku --trials 10
uv run python -m surface_bench.report results/<timestamp>
```

> Prefer plain pip? `pip install -e .` then drop the `uv run` prefix — everything still works.

**Polyglot scenarios.** Code-edit scenarios graded with `node --test` (e.g. the TypeScript
`pagination-ts-code`) need **Node ≥ 22.18** on `PATH` — that is the first release where TypeScript
type-stripping is on by default, so the agent's `.ts` runs with no `npm install` or `tsc` step.
uv does not manage Node; install it separately.

## Authoring a scenario

1. Write `code/` (the **drifted/T1** state the agent sees) and `.author/code_t0/` (the pre-drift
   files that differ — usually just the anchored symbol).
2. Write `hub_stale.md` (describes T0) and `hub_fresh.md` (describes T1), both anchoring the same
   symbol; leave `hash: 000000000000`.
3. Write `task.md`. **QA:** end with a `VERDICT:` line the rubric parses. **code-edit:** ask for
   full files in `FILE: <path>` blocks.
4. Write the grader: `grader/rubric.toml` (QA) or `grader/grader.toml` + `grader/tests/` (code).
5. `python tools/author.py scenarios/<id>` — seals both hubs against the real binary and emits the
   genuine `surf_report.json`. It fails if the stale hub doesn't actually diverge.

Keep the correct answer **non-obvious from a quick code read**, or the documentation carries no
weight and the bench measures nothing.

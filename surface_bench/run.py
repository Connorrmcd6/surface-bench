"""Matrix runner: scenario x condition x model x trial -> results/<ts>/raw.jsonl.

Each row is one model call plus its deterministic grade. Raw output is preserved so grading can
be re-run offline without re-spending tokens.

    python -m surface_bench.run --models mock
    python -m surface_bench.run --models haiku --scenarios refresh-single-use-qa --trials 10
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from . import grade_code, grade_qa
from .agent import run_agent
from .models import build_model
from .prompts import CONDITIONS, build_prompt
from .scenarios import discover
from .tools_runtime import ToolContext, scenario_sandbox, touched_hidden

BENCH_ROOT = Path(__file__).resolve().parent.parent


def _surf_version() -> str:
    for cand in ("target/release/surf", "target/debug/surf"):
        p = BENCH_ROOT.parent / cand
        if p.exists():
            out = subprocess.run([str(p), "--version"], capture_output=True, text=True)
            return out.stdout.strip()
    return "unknown"


def _grade(scenario, output: str) -> dict:
    if scenario.task_type == "qa":
        return grade_qa.grade(scenario, output)
    return grade_code.grade(scenario, output)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(BENCH_ROOT / "config.toml"))
    ap.add_argument("--models", nargs="*", help="subset of configured model names")
    ap.add_argument("--scenarios", nargs="*", help="subset of scenario ids")
    ap.add_argument("--conditions", nargs="*", default=list(CONDITIONS))
    ap.add_argument("--trials", type=int, help="override trials from config")
    ap.add_argument(
        "--mode",
        choices=("single", "multi"),
        help="single-shot completion (v1) or multi-turn tool-using agent (v2)",
    )
    ap.add_argument("--max-turns", type=int, help="agent turn budget in multi mode")
    ap.add_argument("--out", help="results dir (default results/<timestamp>)")
    args = ap.parse_args()

    cfg = tomllib.loads(Path(args.config).read_text())
    trials = args.trials or cfg.get("trials", 10)
    temperature = cfg.get("temperature", 1.0)
    max_tokens = cfg.get("max_tokens", 1024)
    mode = args.mode or cfg.get("mode", "single")
    max_turns = args.max_turns or cfg.get("max_turns", 8)
    model_specs = cfg.get("models", {})
    model_names = args.models or list(model_specs)

    scenarios = discover(BENCH_ROOT / "scenarios", only=args.scenarios)
    if not scenarios:
        sys.exit("no scenarios matched")

    models = {
        n: build_model(
            n, model_specs[n], temperature=temperature, max_tokens=max_tokens, mode=mode
        )
        for n in model_names
    }
    mock_names = {n for n in model_names if model_specs[n].get("provider") == "mock"}
    if mode == "multi":
        missing = [n for n, m in models.items() if not hasattr(m, "step")]
        if missing:
            sys.exit(f"multi mode needs a tool-using model; {missing} have no step() yet")
    # USD per token, per model (from config; 0 if unpriced, e.g. the mock).
    pricing = {
        n: (
            model_specs[n].get("input_per_mtok", 0.0) / 1e6,
            model_specs[n].get("output_per_mtok", 0.0) / 1e6,
        )
        for n in model_names
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out) if args.out else BENCH_ROOT / "results" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"

    meta = {
        "timestamp": ts,
        "trials": trials,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "max_turns": max_turns if mode == "multi" else None,
        "conditions": args.conditions,
        "models": {n: model_specs[n] for n in model_names},
        "scenarios": [s.id for s in scenarios],
        "surf_version": _surf_version(),
    }
    (out_dir / "run.json").write_text(json.dumps(meta, indent=2) + "\n")

    n_total = len(scenarios) * len(args.conditions) * len(models) * trials
    done = 0
    with raw_path.open("w") as fh:
        for scenario in scenarios:
            for condition in args.conditions:
                system, user = build_prompt(scenario, condition)
                for model_name, model in models.items():
                    if hasattr(model, "set_condition"):
                        model.set_condition(condition)
                    for trial in range(trials):
                        row = {
                            "scenario": scenario.id,
                            "task_type": scenario.task_type,
                            "tier": scenario.tier,
                            "condition": condition,
                            "model": model_name,
                            "trial": trial,
                            "mode": mode,
                        }
                        try:
                            if mode == "multi":
                                # Fresh per-trial sandbox: the agent's tools can reach the hidden
                                # dependency that the prompt withholds.
                                with scenario_sandbox(scenario) as ws:
                                    traj = run_agent(
                                        model, system, user, ToolContext(ws), max_turns=max_turns
                                    )
                                text, in_tok, out_tok = (
                                    traj.final_text,
                                    traj.input_tokens,
                                    traj.output_tokens,
                                )
                                agent_fields = dict(
                                    turns=traj.turns,
                                    stop_reason=traj.stop_reason,
                                    tool_calls=traj.tool_calls,
                                    verified_hidden=touched_hidden(
                                        traj.accessed, scenario.hidden_paths
                                    ),
                                    per_turn_tokens=traj.per_turn_tokens,
                                )
                            else:
                                comp = model.complete(system, user)
                                text, in_tok, out_tok = (
                                    comp.text,
                                    comp.input_tokens,
                                    comp.output_tokens,
                                )
                                agent_fields = {}
                            grade = _grade(scenario, text)
                            in_price, out_price = pricing[model_name]
                            row.update(
                                output=text,
                                input_tokens=in_tok,
                                output_tokens=out_tok,
                                cost_usd=in_tok * in_price + out_tok * out_price,
                                ok=grade["ok"],
                                misled=grade["misled"],
                                detail=grade["detail"],
                                parsed=grade["parsed"],
                                **agent_fields,
                            )
                        except Exception as e:  # keep the matrix going; record the failure
                            row.update(output=None, ok=False, misled=False, error=repr(e))
                        fh.write(json.dumps(row) + "\n")
                        fh.flush()
                        done += 1
                        print(
                            f"\r[{done}/{n_total}] {scenario.id} {condition} {model_name}",
                            end="",
                            file=sys.stderr,
                        )
                        if model_name not in mock_names:
                            time.sleep(0)  # placeholder for rate-limit backoff hook
    print(f"\nwrote {raw_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

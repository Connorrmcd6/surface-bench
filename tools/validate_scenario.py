"""Offline grader-polarization self-test for a scenario (no API, no spend).

`tools/author.py` seals hubs and proves the *drift* is real; it does NOT prove the *graders*
discriminate. The biggest risk across many fixtures is a mis-polarized grader — `check_correct` and
`check_misled` both passing, both failing, or swapped — which only the post-run oracle would catch,
and only after spending tokens. This tool closes that gap before any spend.

Each scenario ships two reference solutions in `.author/`:
  * solution_correct.<ext>  — implements the CURRENT (T1) behaviour (or, for QA, ends in the correct
                              VERDICT line). Must grade ok=True, misled=False.
  * solution_stale.<ext>    — implements the STALE (T0) doc's value (or the misled VERDICT). Must
                              grade ok=False, misled=True.
We feed each through the LIVE graders (`grade_code.grade` / `grade_qa.grade`), so the self-test
exercises the exact path the real run uses. A scenario passes only if both polarities hold.

    python tools/validate_scenario.py scenarios/<id>
    python tools/validate_scenario.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BENCH_ROOT))

from surface_bench import grade_code, grade_qa  # noqa: E402
from surface_bench.scenarios import Scenario, load_scenario  # noqa: E402

_FENCE = {"python": "python", "typescript": "typescript", "tsx": "tsx", "javascript": "javascript"}


def _solution(scenario: Scenario, which: str) -> Path:
    hits = sorted((scenario.root / ".author").glob(f"solution_{which}.*"))
    if not hits:
        raise SystemExit(f"{scenario.id}: missing .author/solution_{which}.* reference solution")
    if len(hits) > 1:
        raise SystemExit(f"{scenario.id}: multiple .author/solution_{which}.* files: {hits}")
    return hits[0]


def _code_output(scenario: Scenario, body: str) -> str:
    if not scenario.edit_path:
        raise SystemExit(f"{scenario.id}: code scenario needs `edit_path` in meta.toml")
    fence = _FENCE.get(scenario.lang, "")
    return f"FILE: {scenario.edit_path}\n```{fence}\n{body.rstrip()}\n```\n"


def _grade(scenario: Scenario, which: str) -> dict:
    body = _solution(scenario, which).read_text()
    if scenario.task_type == "code":
        return grade_code.grade(scenario, _code_output(scenario, body))
    return grade_qa.grade(scenario, body)  # QA: the .txt is the agent's verbatim answer


def validate(scenario: Scenario) -> list[str]:
    """Return a list of polarization failures (empty == passes)."""
    fails: list[str] = []
    correct = _grade(scenario, "correct")
    if not (correct["ok"] and not correct["misled"]):
        fails.append(
            f"solution_correct graded ok={correct['ok']} misled={correct['misled']} "
            f"(want ok=True, misled=False) — {correct.get('detail')}"
        )
    stale = _grade(scenario, "stale")
    if not (not stale["ok"] and stale["misled"]):
        fails.append(
            f"solution_stale graded ok={stale['ok']} misled={stale['misled']} "
            f"(want ok=False, misled=True) — {stale.get('detail')}"
        )
    return fails


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?", help="path to a scenario dir")
    ap.add_argument("--all", action="store_true", help="validate every scenario with reference solutions")
    args = ap.parse_args()

    if args.all:
        dirs = sorted(p.parent for p in (BENCH_ROOT / "scenarios").glob("*/meta.toml"))
        targets = [d for d in dirs if list((d / ".author").glob("solution_correct.*"))]
    elif args.scenario:
        targets = [Path(args.scenario).resolve()]
    else:
        ap.error("pass a scenario dir or --all")

    failed = 0
    for d in targets:
        scenario = load_scenario(d)
        fails = validate(scenario)
        if fails:
            failed += 1
            print(f"FAIL {scenario.id}")
            for f in fails:
                print(f"     - {f}")
        else:
            print(f"ok   {scenario.id}")
    if failed:
        sys.exit(f"\n{failed} scenario(s) failed grader polarization")
    print(f"\nall {len(targets)} scenario(s) pass grader polarization")


if __name__ == "__main__":
    main()

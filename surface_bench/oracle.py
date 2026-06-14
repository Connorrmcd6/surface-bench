"""Post-run sanity tripwires for a results dir — cheap checks that catch authoring/harness bugs
before they reach the write-up (the failure mode recorded in issue #113).

    python -m surface_bench.oracle results/<timestamp>

Checks (per scenario x model):
  * C2-fresh ≈ 100% — with a *fresh* doc and the code readable, the task must be solvable; a low
    cell means the scenario is mis-authored (a leaked stale value, a broken grader, an impossible
    task), not a real effect.
  * cascade C1 misleads at all — if a stale doc never produces the wrong answer, the drift isn't
    load-bearing and the scenario measures nothing.

The surf_report `changed` divergence is sealed at authoring time by tools/author.py, so it isn't
re-checked here. Exit code is non-zero if any tripwire fires, so this can gate a run in CI.
"""

from __future__ import annotations

import sys

from .metrics import load_rows

C2_FRESH_THRESHOLD = 0.9


def check(rows: list[dict], *, c2_threshold: float = C2_FRESH_THRESHOLD) -> list[str]:
    warnings: list[str] = []
    scenarios = sorted({r["scenario"] for r in rows})
    models = sorted({r["model"] for r in rows})
    for sc in scenarios:
        for m in models:
            def cell(cond: str) -> list[dict]:
                return [
                    r for r in rows if r["scenario"] == sc and r["model"] == m and r["condition"] == cond
                ]

            c2 = cell("C2")
            if c2:
                sr = sum(bool(r.get("ok")) for r in c2) / len(c2)
                if sr < c2_threshold:
                    warnings.append(
                        f"C2-fresh low: {sc} / {m} = {sr:.0%} (< {c2_threshold:.0%}) "
                        "— likely an authoring bug, not a real effect"
                    )
            if sc.startswith("cascade-"):
                c1 = cell("C1")
                if c1 and not any(r.get("misled") for r in c1):
                    warnings.append(
                        f"C1 never misleads: {sc} / {m} — the drift may not be load-bearing"
                    )
    return warnings


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python -m surface_bench.oracle results/<timestamp>")
    warnings = check(load_rows(sys.argv[1]))
    if not warnings:
        print("oracle: PASS — all tripwires clear")
        return
    print(f"oracle: {len(warnings)} warning(s):")
    for w in warnings:
        print(f"  - {w}")
    sys.exit(1)


if __name__ == "__main__":
    main()

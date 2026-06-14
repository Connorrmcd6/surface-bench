"""Guard the committed scenario set: every scenario shipping reference solutions must have
correctly-polarized graders (correct -> ok & not misled; stale -> not ok & misled). Runs the live
graders via the validate_scenario tool — offline, no API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BENCH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_ROOT / "tools"))

import validate_scenario  # noqa: E402

from surface_bench.scenarios import load_scenario  # noqa: E402


def _scenarios_with_solutions() -> list[Path]:
    dirs = sorted(p.parent for p in (BENCH_ROOT / "scenarios").glob("*/meta.toml"))
    return [d for d in dirs if list((d / ".author").glob("solution_correct.*"))]


@pytest.mark.parametrize("scenario_dir", _scenarios_with_solutions(), ids=lambda d: d.name)
def test_grader_polarization(scenario_dir: Path) -> None:
    fails = validate_scenario.validate(load_scenario(scenario_dir))
    assert not fails, "; ".join(fails)


def test_at_least_the_new_cascades_are_covered() -> None:
    covered = {d.name for d in _scenarios_with_solutions()}
    expected = {
        "cascade-ttl-units-code",
        "cascade-money-rounding-code",
        "cascade-backoff-offbyone-code",
        "cascade-signal-threshold-code",
    }
    assert expected <= covered, f"missing reference solutions for {expected - covered}"

"""Offline tests for the Cw control (phase 5) and the verification metrics / Holm / per-scenario /
oracle layer (phase 6)."""

from __future__ import annotations

from pathlib import Path

from surface_bench import oracle
from surface_bench.metrics import summarize
from surface_bench.prompts import CONDITIONS, build_prompt
from surface_bench.scenarios import load_scenario

BENCH_ROOT = Path(__file__).resolve().parents[1]


# ---- Phase 5: Cw control --------------------------------------------------------------------


def test_cw_condition_is_stale_plus_generic_warning_only() -> None:
    assert "Cw" in CONDITIONS
    scenario = load_scenario(BENCH_ROOT / "scenarios" / "cascade-quota-batcher-code")
    _, cw = build_prompt(scenario, "Cw")
    _, c1 = build_prompt(scenario, "C1")
    _, c3 = build_prompt(scenario, "C3")

    # Cw = the stale hub (like C1) + a generic warning, but WITHOUT surf's corrected code (unlike C3).
    assert scenario.hub_stale.strip()[:40] in cw  # carries the stale doc
    assert "may be out of date" in cw
    assert "Automated documentation check" not in cw  # no surf report
    assert "new_code" not in cw  # no corrected value leaked
    assert cw != c1 and cw != c3


# ---- Phase 6: verification metrics ----------------------------------------------------------


def _row(sc, cond, ok, misled, ver=None, tok=100):
    r = {
        "scenario": sc,
        "model": "m",
        "condition": cond,
        "tier": "T1",
        "ok": ok,
        "misled": misled,
        "output_tokens": tok,
    }
    if ver is not None:
        r["verified_hidden"] = ver
    return r


def _multi_rows():
    rows = []
    sc = "cascade-x"
    rows += [_row(sc, "C0", True, False, ver=True) for _ in range(10)]  # no doc -> verifies, correct
    # stale doc -> mostly skips verification; verifiers right, non-verifiers misled (H5)
    rows += [_row(sc, "C1", True, False, ver=True) for _ in range(2)]
    rows += [_row(sc, "C1", False, True, ver=False) for _ in range(8)]
    rows += [_row(sc, "C2", True, False, ver=False) for _ in range(10)]  # fresh -> correct
    rows += [_row(sc, "C3", True, False, ver=False) for _ in range(10)]  # surf report -> correct
    rows += [_row(sc, "Cw", False, True, ver=False) for _ in range(10)]  # bare warning -> no help
    return rows


def test_verification_block_and_mediation() -> None:
    s = summarize(_multi_rows())
    assert "verification" in s
    ver = s["verification"]["m"]
    assert ver["C0"]["verification_rate"] == 1.0
    assert ver["C1"]["verification_rate"] == 0.2
    # H4: a stale doc suppresses verification vs no doc
    assert s["verification_deltas"]["m"]["C0-C1"]["delta"] > 0
    # H5 mediation: within C1 verifiers are correct, non-verifiers are not
    med = s["mediation"]["m"]
    assert med["verified_success"] == 1.0 and med["n_verified"] == 2
    assert med["unverified_success"] == 0.0 and med["n_unverified"] == 8


def test_cw_pairs_and_holm_on_success_deltas() -> None:
    s = summarize(_multi_rows())
    d = s["deltas"]["m"]
    assert "C3-Cw" in d and "Cw-C1" in d  # the control contrasts
    assert d["C3-Cw"]["delta"] > 0  # surf's fix beats a bare warning
    for entry in d.values():
        assert "p" in entry and "significant_holm" in entry


def test_per_scenario_breakdown_carries_verification() -> None:
    s = summarize(_multi_rows())
    cell = s["by_scenario"]["cascade-x"]["m"]["C0"]
    assert cell["success"] == 1.0
    assert cell["verification_rate"] == 1.0


# ---- Phase 6: oracle tripwires --------------------------------------------------------------


def test_oracle_passes_clean_run() -> None:
    assert oracle.check(_multi_rows()) == []


def test_oracle_flags_low_c2_and_non_misleading_cascade() -> None:
    rows = []
    rows += [_row("cascade-broken", "C2", False, False, ver=False) for _ in range(10)]  # C2 fail
    rows += [_row("cascade-inert", "C1", False, False, ver=False) for _ in range(10)]  # never misleads
    rows += [_row("cascade-inert", "C2", True, False, ver=False) for _ in range(10)]
    warnings = oracle.check(rows)
    assert any("C2-fresh low" in w and "cascade-broken" in w for w in warnings)
    assert any("never misleads" in w and "cascade-inert" in w for w in warnings)

"""Generate a scenario's authentic Surface artifacts with the real `surf` binary.

For a scenario dir it (re)produces, all from the committed inputs:

  * hub_fresh.md  -> stored hash sealed against the CURRENT code/ (so it verifies clean)
  * hub_stale.md  -> stored hash sealed against the PRE-DRIFT .author/code_t0/ overlay
                     (so it reads as DIVERGED against code/)
  * surf_report.json -> the genuine `surf check --format json` output for the stale hub
                        vs the current code/ (this is the C3 context the agent sees)

This keeps the bench honest: the divergence the agent is shown is one the shipped gate emits,
not a hand-written mock. Re-run after editing a scenario's code or hubs.

Usage:
    python tools/author.py scenarios/<id>            # one scenario
    python tools/author.py --all                     # every scenario under scenarios/
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BENCH_ROOT.parent


def find_surf() -> str:
    for cand in (REPO_ROOT / "target/release/surf", REPO_ROOT / "target/debug/surf"):
        if cand.exists():
            return str(cand)
    found = shutil.which("surf")
    if found:
        return found
    sys.exit("could not find a `surf` binary (build it: cargo build --release)")


def _seal(surf: str, workdir: Path) -> None:
    """Run `surf verify` in workdir, rewriting hub.md's stored hash in place."""
    subprocess.run([surf, "verify"], cwd=workdir, check=True, capture_output=True, text=True)


def _read_hash(hub: Path) -> str:
    m = re.search(r"^\s*hash:\s*([0-9a-f]+)\s*$", hub.read_text(), re.MULTILINE)
    if not m:
        sys.exit(f"no hash found in {hub} after verify")
    return m.group(1)


def _write_hash(hub: Path, new_hash: str) -> None:
    text = re.sub(
        r"^(\s*hash:\s*)[0-9a-f]+(\s*)$",
        rf"\g<1>{new_hash}\g<2>",
        hub.read_text(),
        count=1,
        flags=re.MULTILINE,
    )
    hub.write_text(text)


def _fresh_workspace(scenario: Path, tmp: Path, *, t0: bool) -> None:
    """Lay out a surf workspace in tmp: current code/ (optionally T0-overlaid) + surf.toml."""
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(scenario / "code", tmp / "code")
    if t0:
        overlay = scenario / ".author" / "code_t0"
        if overlay.is_dir():
            for src in overlay.rglob("*"):
                if src.is_file():
                    dst = tmp / "code" / src.relative_to(overlay)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
    (tmp / "surf.toml").write_text('hubs = ["hub.md"]\n')


def author(scenario: Path, surf: str) -> None:
    meta = tomllib.loads((scenario / "meta.toml").read_text())
    tmp = scenario / ".author" / ".work"

    # 1) Fresh hub: seal against the current (drifted) code -> verifies clean.
    _fresh_workspace(scenario, tmp, t0=False)
    shutil.copy2(scenario / "hub_fresh.md", tmp / "hub.md")
    _seal(surf, tmp)
    _write_hash(scenario / "hub_fresh.md", _read_hash(tmp / "hub.md"))

    # 2) Stale hub: seal against the PRE-DRIFT code -> its hash no longer matches code/.
    _fresh_workspace(scenario, tmp, t0=True)
    shutil.copy2(scenario / "hub_stale.md", tmp / "hub.md")
    _seal(surf, tmp)
    stale_hash = _read_hash(tmp / "hub.md")
    _write_hash(scenario / "hub_stale.md", stale_hash)

    # 3) Genuine divergence report: stale hub (T0 hash) checked against current code/.
    _fresh_workspace(scenario, tmp, t0=False)
    shutil.copy2(scenario / "hub_stale.md", tmp / "hub.md")
    proc = subprocess.run(
        [surf, "check", "--format", "json"], cwd=tmp, capture_output=True, text=True
    )
    report = json.loads(proc.stdout)
    divs = report.get("divergences", [])
    if not any(d.get("kind") == "changed" for d in divs):
        sys.exit(
            f"{scenario.name}: expected a 'changed' divergence for the stale hub but got "
            f"{json.dumps(divs)} — check the drift in code/ vs .author/code_t0/."
        )
    (scenario / "surf_report.json").write_text(json.dumps(report, indent=2) + "\n")

    shutil.rmtree(tmp)
    print(f"authored {scenario.name}: stale={stale_hash} fresh={_read_hash(scenario / 'hub_fresh.md')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?", help="path to a scenario dir")
    ap.add_argument("--all", action="store_true", help="author every scenario")
    args = ap.parse_args()

    surf = find_surf()
    if args.all:
        targets = sorted(p.parent for p in (BENCH_ROOT / "scenarios").glob("*/meta.toml"))
    elif args.scenario:
        targets = [Path(args.scenario).resolve()]
    else:
        ap.error("pass a scenario dir or --all")

    for scenario in targets:
        author(scenario, surf)


if __name__ == "__main__":
    main()

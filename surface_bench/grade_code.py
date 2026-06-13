"""Deterministic grading for code-edit scenarios.

The agent returns the full contents of each file it changes, each fenced block preceded by a
`FILE: <path>` line. We overlay those onto a fresh copy of code/, drop in the hidden grader
tests, and run two commands defined in grader/grader.toml:

  * correct_cmd — exit 0 iff the CURRENT (T1) behaviour is implemented   -> ok
  * misled_cmd  — exit 0 iff the STALE (T0) behaviour was implemented     -> misled

Running real tests against the applied patch means the primary metric has zero judge noise.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

from .scenarios import Scenario

_FILE_BLOCK = re.compile(
    r"^FILE:\s*(?P<path>\S+)\s*?\n```[^\n]*\n(?P<body>.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def parse_files(output: str) -> dict[str, str]:
    return {m.group("path").strip(): m.group("body") for m in _FILE_BLOCK.finditer(output)}


def _run(cmd: list[str], cwd: Path) -> bool:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    return proc.returncode == 0


def grade(scenario: Scenario, output: str) -> dict:
    grader = tomllib.loads((scenario.grader_dir / "grader.toml").read_text())
    files = parse_files(output)
    if not files:
        return {"ok": False, "misled": False, "parsed": {}, "detail": "no FILE blocks in output"}

    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        shutil.copytree(scenario.root / "code", ws / "code")

        # Overlay the agent's files. Paths are relative to the workspace root (e.g. code/...).
        applied = []
        for rel, body in files.items():
            dst = ws / rel
            if scenario.root.resolve() not in (ws / rel).resolve().parents and not str(
                (ws / rel).resolve()
            ).startswith(str(ws.resolve())):
                continue  # guard against path escapes
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(body if body.endswith("\n") else body + "\n")
            applied.append(rel)

        for rel in grader.get("setup_files", []):
            src = scenario.grader_dir / rel
            dst = ws / rel
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        ok = _run(grader["correct_cmd"], ws)
        misled = False
        if "misled_cmd" in grader:
            misled = _run(grader["misled_cmd"], ws)

    return {
        "ok": ok,
        "misled": misled,
        "parsed": {"applied": applied},
        "detail": "correct test passed" if ok else "correct test failed",
    }

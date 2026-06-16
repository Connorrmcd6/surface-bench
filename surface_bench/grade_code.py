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
import sys
import tempfile
import tomllib
from pathlib import Path

from .scenarios import Scenario

_FILE_BLOCK = re.compile(
    r"^FILE:\s*(?P<path>\S+)\s*?\n```[^\n]*\n(?P<body>.*?)\n```",
    re.MULTILINE | re.DOTALL,
)

# Fallback: a `FILE: <path>` line followed by an UNFENCED body (the model produced correct file
# contents but dropped the ``` fence). Body runs to the next FILE: marker or end of output. Used
# ONLY when no fenced block parses, so the fenced contract stays primary and a well-formed answer is
# never reinterpreted. This is a parser-leniency change — it never touches scenarios or grading — so
# it cannot bias the result toward any condition; it only stops penalising correct work for a
# cosmetic formatting miss.
_FILE_UNFENCED = re.compile(
    r"^FILE:\s*(?P<path>\S+)[ \t]*\n(?P<body>.*?)(?=^FILE:|\Z)",
    re.MULTILINE | re.DOTALL,
)


def parse_files(output: str) -> dict[str, str]:
    files = {m.group("path").strip(): m.group("body") for m in _FILE_BLOCK.finditer(output)}
    if files:
        return files
    out: dict[str, str] = {}
    for m in _FILE_UNFENCED.finditer(output):
        body = m.group("body")
        # Defensively strip a stray opening/closing fence if the model half-fenced the block.
        body = re.sub(r"\A```[^\n]*\n", "", body)
        body = re.sub(r"\n```[ \t]*\Z", "\n", body)
        out[m.group("path").strip()] = body.rstrip("\n")
    return out


def _run(cmd: list[str], cwd: Path) -> bool:
    # Run a "python"/"python3" grader command under the *same* interpreter as the harness, so the
    # check inherits whatever env launched the run (uv, venv, system) rather than gambling on which
    # `python3` happens to be on PATH. Other commands (e.g. `node`) are resolved from PATH as-is.
    if cmd and cmd[0] in ("python", "python3"):
        cmd = [sys.executable, *cmd[1:]]
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

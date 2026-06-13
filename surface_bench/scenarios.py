"""Load and validate a scenario directory into an in-memory Scenario."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Files in code/ we never show the agent (caches, compiled output).
_SKIP = {".pyc", ".pyo"}
_SKIP_DIRS = {"__pycache__", "node_modules", ".git"}


@dataclass(frozen=True)
class CodeFile:
    relpath: str  # path relative to the scenario's code/ root, forward-slashed
    content: str


@dataclass
class Scenario:
    id: str
    title: str
    lang: str
    task_type: str  # "qa" | "code"
    tier: str  # complexity tier: T0 local | T1 buried | T2 premise | T3 multi-claim
    anchor: str
    invariant: str
    root: Path
    task: str
    hub_stale: str
    hub_fresh: str
    surf_report: str  # raw JSON text of the genuine `surf check` divergence
    code: list[CodeFile] = field(default_factory=list)
    # code/ paths (or globs) present for grading but withheld from the prompt — the hidden
    # dependency in a cascade scenario, which the agent knows only through its doc.
    hidden_paths: list[str] = field(default_factory=list)

    @property
    def grader_dir(self) -> Path:
        return self.root / "grader"


def _read_code(code_root: Path) -> list[CodeFile]:
    files: list[CodeFile] = []
    for p in sorted(code_root.rglob("*")):
        if not p.is_file() or p.suffix in _SKIP:
            continue
        if any(part in _SKIP_DIRS for part in p.relative_to(code_root).parts):
            continue
        rel = p.relative_to(code_root).as_posix()
        files.append(CodeFile(relpath=f"code/{rel}", content=p.read_text()))
    return files


def load_scenario(path: str | Path) -> Scenario:
    root = Path(path).resolve()
    meta = tomllib.loads((root / "meta.toml").read_text())
    required = {"id", "title", "lang", "task_type", "anchor"}
    missing = required - meta.keys()
    if missing:
        raise ValueError(f"{root}: meta.toml missing keys {sorted(missing)}")
    if meta["task_type"] not in ("qa", "code"):
        raise ValueError(f"{root}: task_type must be 'qa' or 'code'")

    return Scenario(
        id=meta["id"],
        title=meta["title"],
        lang=meta["lang"],
        task_type=meta["task_type"],
        tier=meta.get("tier", "T0"),
        anchor=meta["anchor"],
        invariant=meta.get("invariant", ""),
        root=root,
        task=(root / "task.md").read_text(),
        hub_stale=(root / "hub_stale.md").read_text(),
        hub_fresh=(root / "hub_fresh.md").read_text(),
        surf_report=(root / "surf_report.json").read_text(),
        code=_read_code(root / "code"),
        hidden_paths=meta.get("hidden_paths", []),
    )


def discover(scenarios_dir: str | Path, only: list[str] | None = None) -> list[Scenario]:
    base = Path(scenarios_dir)
    dirs = sorted(p.parent for p in base.glob("*/meta.toml"))
    scenarios = [load_scenario(d) for d in dirs]
    if only:
        wanted = set(only)
        scenarios = [s for s in scenarios if s.id in wanted]
    return scenarios

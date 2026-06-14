"""Read-only tool surface for the multi-turn agent loop (v2 / milestone #12).

The agentic track gives the model tools so it can *choose* to read the dependency a doc describes,
instead of being forced to trust the doc (the single-shot cascade's structural limit). The whole
point is to measure whether a confident *stale* doc suppresses that verification — so the surface is
deliberately **read-only**: `read_file`, `grep`, `list_dir`, and a `final_answer` terminator. There is
no `run_tests`/shell: a test runner would let the agent brute-force ground truth and wash out the
doc-trust signal we are trying to measure.

Tools are scoped to a per-trial sandbox (see `scenario_sandbox`): a fresh copy of the scenario's
`code/` tree that **includes the hidden dependency**. The initial prompt still omits `hidden_paths`
(`prompts._render_code`), but the file is on disk, so `read_file("code/limiter/window.py")` succeeds
— the hidden truth is reachable *by choice, not absent*. Every path is resolved inside the sandbox;
escapes (`..`, absolute paths) are rejected.

`TOOL_SPECS` is provider-neutral: a list of `{name, description, parameters}` (parameters is a JSON
Schema). Each model adapter translates it into its own tool format (Anthropic `input_schema`, OpenAI
`function.parameters`, Gemini `FunctionDeclaration`), so `agent.py` and the graders never learn which
provider ran.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path

from .scenarios import Scenario

# Bound a single tool result so one huge file can't blow the turn's token budget. Fixtures are tiny;
# this only guards against pathological inputs.
MAX_READ_BYTES = 64 * 1024
MAX_GREP_MATCHES = 100


class ToolError(Exception):
    """A tool was called with bad arguments (e.g. a path escape). The message is fed back to the
    model as the tool result so it can recover, rather than crashing the run."""


# Provider-neutral tool schemas. `parameters` is a JSON Schema object; adapters translate it.
TOOL_SPECS: list[dict] = [
    {
        "name": "list_dir",
        "description": "List the files and directories under a workspace-relative path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace-relative directory (default the workspace root).",
                }
            },
            "required": [],
        },
    },
    {
        "name": "read_file",
        "description": "Read the full contents of a workspace-relative file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Workspace-relative file path."}
            },
            "required": ["path"],
        },
    },
    {
        "name": "grep",
        "description": "Search files for a regular expression, returning matching lines as "
        "`path:lineno: line`.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "A Python regular expression."},
                "path": {
                    "type": "string",
                    "description": "Workspace-relative file or directory to search "
                    "(default the workspace root).",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "final_answer",
        "description": "Submit your final answer and end the task. Provide the complete answer "
        "(including any required VERDICT line or FILE: blocks) in `answer`.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The complete final answer."}
            },
            "required": ["answer"],
        },
    },
]

TOOL_NAMES = frozenset(spec["name"] for spec in TOOL_SPECS)


class ToolContext:
    """Executes the read-only tools against a sandbox root and records what was accessed.

    `accessed` is the list of workspace-relative paths the agent actually read or grepped — the raw
    material for the *verification rate* metric (did it read a load-bearing hidden dependency before
    answering?). `final_answer` is set once the agent terminates.
    """

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.accessed: list[str] = []
        self.final_answer: str | None = None

    # -- path safety -------------------------------------------------------------------------
    def _resolve(self, rel: str) -> Path:
        # `root / "/abs"` collapses to "/abs" in pathlib, and `..` walks up — resolve() then makes
        # any escape visible, and we reject anything not inside the sandbox.
        p = (self.root / rel).resolve()
        if p != self.root and self.root not in p.parents:
            raise ToolError(f"path {rel!r} escapes the workspace")
        return p

    def _rel(self, p: Path) -> str:
        return p.relative_to(self.root).as_posix()

    # -- tools -------------------------------------------------------------------------------
    def list_dir(self, path: str = ".") -> str:
        p = self._resolve(path)
        if not p.exists():
            raise ToolError(f"no such path: {path!r}")
        if not p.is_dir():
            raise ToolError(f"not a directory: {path!r}")
        names = sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir())
        return "\n".join(names) if names else "(empty)"

    def read_file(self, path: str) -> str:
        p = self._resolve(path)
        if not p.is_file():
            raise ToolError(f"no such file: {path!r}")
        self.accessed.append(self._rel(p))
        data = p.read_bytes()
        truncated = len(data) > MAX_READ_BYTES
        text = data[:MAX_READ_BYTES].decode("utf-8", errors="replace")
        if truncated:
            text += f"\n... [truncated at {MAX_READ_BYTES} bytes]"
        return text

    def grep(self, pattern: str, path: str = ".") -> str:
        try:
            rx = re.compile(pattern)
        except re.error as e:
            raise ToolError(f"invalid regex: {e}") from e
        p = self._resolve(path)
        if not p.exists():
            raise ToolError(f"no such path: {path!r}")
        files = [p] if p.is_file() else [f for f in sorted(p.rglob("*")) if f.is_file()]
        matches: list[str] = []
        for f in files:
            rel = self._rel(f)
            try:
                lines = f.read_text(errors="replace").splitlines()
            except OSError:
                continue
            hit = False
            for i, line in enumerate(lines, 1):
                if rx.search(line):
                    matches.append(f"{rel}:{i}: {line}")
                    hit = True
                    if len(matches) >= MAX_GREP_MATCHES:
                        break
            if hit:
                self.accessed.append(rel)
            if len(matches) >= MAX_GREP_MATCHES:
                matches.append("... [more matches truncated]")
                break
        return "\n".join(matches) if matches else "(no matches)"

    def submit(self, answer: str) -> str:
        self.final_answer = answer
        return "Final answer recorded."

    # -- verification metric helper ----------------------------------------------------------
    def verified(self, hidden_paths: list[str]) -> bool:
        """True iff the agent read/grepped a file matching one of the scenario's hidden globs —
        i.e. it went and checked the dependency the (possibly stale) doc describes."""
        return touched_hidden(self.accessed, hidden_paths)


def touched_hidden(accessed: list[str], hidden_paths: list[str]) -> bool:
    """Did any accessed path match a hidden glob? The basis of the verification-rate metric; lives
    at module scope so the runner can compute it from a `Trajectory.accessed` list without a ctx."""
    return any(fnmatch(a, pat) for a in accessed for pat in hidden_paths)


def dispatch(name: str, args: dict, ctx: ToolContext) -> tuple[str, bool]:
    """Run one tool call. Returns `(result_text, is_final)`. Bad calls return an error string (not
    an exception) so the loop can feed it back and let the model recover."""
    try:
        if name == "list_dir":
            return ctx.list_dir(args.get("path", ".")), False
        if name == "read_file":
            return ctx.read_file(args["path"]), False
        if name == "grep":
            return ctx.grep(args["pattern"], args.get("path", ".")), False
        if name == "final_answer":
            return ctx.submit(args["answer"]), True
        return f"error: unknown tool {name!r}", False
    except KeyError as e:
        return f"error: missing required argument {e}", False
    except ToolError as e:
        return f"error: {e}", False


@contextmanager
def scenario_sandbox(scenario: Scenario) -> Iterator[Path]:
    """Yield a fresh per-trial workspace root containing a copy of the scenario's `code/` tree,
    **including the hidden dependency**. A `ToolContext(root)` scoped here can read any file the
    grader runs against, while the prompt still omits `hidden_paths`."""
    with tempfile.TemporaryDirectory(prefix=f"surfbench-{scenario.id}-") as td:
        ws = Path(td)
        shutil.copytree(scenario.root / "code", ws / "code")
        yield ws

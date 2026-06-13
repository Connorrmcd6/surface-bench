"""Deterministic grading for QA scenarios.

The agent ends its answer with a structured VERDICT line; the rubric (grader/rubric.toml) names
the fields to extract and the values that count as correct (current/T1 behaviour) versus misled
(the stale/T0 claim). No model judge: parsing a fixed-format line is robust to negation, which
free-text keyword matching is not.
"""

from __future__ import annotations

import re
import tomllib

from .scenarios import Scenario


def _extract(pattern: str, text: str) -> str | None:
    # Last match wins: if the model restates the format in prose then prints the real verdict,
    # the trailing one is authoritative.
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return matches[-1].lower() if matches else None


def grade(scenario: Scenario, output: str) -> dict:
    rubric = tomllib.loads((scenario.grader_dir / "rubric.toml").read_text())
    if rubric.get("type") != "verdict":
        raise ValueError(f"{scenario.id}: unsupported qa rubric type {rubric.get('type')!r}")

    parsed: dict[str, str | None] = {}
    for field_name, spec in rubric["fields"].items():
        parsed[field_name] = _extract(spec["pattern"], output)

    if any(v is None for v in parsed.values()):
        missing = [k for k, v in parsed.items() if v is None]
        return {
            "ok": False,
            "misled": False,
            "parsed": parsed,
            "detail": f"could not parse verdict field(s): {', '.join(missing)}",
        }

    correct = rubric["correct"]
    misled_vals = rubric.get("misled", {})
    ok = all(parsed[k] == v for k, v in correct.items())
    misled = any(parsed.get(k) == v for k, v in misled_vals.items())
    return {
        "ok": ok,
        "misled": misled,
        "parsed": parsed,
        "detail": "correct" if ok else f"verdict {parsed} != expected {correct}",
    }

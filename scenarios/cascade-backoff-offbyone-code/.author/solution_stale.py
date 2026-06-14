"""Reference STALE solution: trusts the doc's 1-based attempts (the misled answer)."""

BASE_MS = 100


def delays(attempts: list[int]) -> list[int]:
    return [BASE_MS << (a - 1) for a in attempts]

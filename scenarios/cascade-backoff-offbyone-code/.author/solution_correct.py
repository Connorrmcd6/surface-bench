"""Reference CORRECT solution: 0-based attempts, matching the real delay_for."""

BASE_MS = 100


def delays(attempts: list[int]) -> list[int]:
    return [BASE_MS << a for a in attempts]

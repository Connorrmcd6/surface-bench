"""Reference STALE solution: trusts the doc's alert-on-rise rule (the misled answer)."""


def should_page(readings: list[float]) -> bool:
    return any(readings[i] - readings[i - 1] > 0 for i in range(1, len(readings)))

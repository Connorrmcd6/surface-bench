"""Reference CORRECT solution: pages on a drop, matching the real is_alerting."""


def should_page(readings: list[float]) -> bool:
    return any(readings[i] - readings[i - 1] < 0 for i in range(1, len(readings)))

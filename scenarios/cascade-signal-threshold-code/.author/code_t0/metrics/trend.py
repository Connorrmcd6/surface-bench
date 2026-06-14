def is_alerting(prev: float, curr: float) -> bool:
    """True when the metric has moved in the direction we page on (a rise from prev to curr)."""
    return curr - prev > 0

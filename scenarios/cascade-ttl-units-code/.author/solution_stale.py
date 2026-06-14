"""Reference STALE solution: trusts the doc's 30-second lifetime (the misled answer)."""

import math


def schedule_refreshes(window_seconds: int) -> int:
    if window_seconds == 0:
        return 0
    return math.ceil(window_seconds / 30)  # stale doc: 30-second lifetime

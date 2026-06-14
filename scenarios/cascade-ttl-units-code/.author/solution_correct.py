"""Reference CORRECT solution: sizes the schedule to the policy's true 5-second lifetime."""

import math


def schedule_refreshes(window_seconds: int) -> int:
    if window_seconds == 0:
        return 0
    return math.ceil(window_seconds / 5)  # real entry lifetime is 5 seconds

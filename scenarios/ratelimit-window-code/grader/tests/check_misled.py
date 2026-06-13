"""Misled (T0) behaviour: the stale doc says "exactly `limit` per window" (exclusive bound).

An agent that trusts the doc over the code computes remaining as `limit - count`, so a fresh key
reports `limit` (== 3) instead of the true `limit + 1` (== 4). We flag that as misled.
"""

import sys

sys.path.insert(0, "code")

from limiter.clock import FixedClock
from limiter.window import FixedWindowLimiter

clock = FixedClock()
lim = FixedWindowLimiter(limit=3, window_seconds=60, clock=clock)

assert lim.remaining("k") == 3, f"fresh remaining={lim.remaining('k')} (stale doc implies 3)"

print("misled: remaining() reports the stale exclusive bound (limit, not limit+1)")

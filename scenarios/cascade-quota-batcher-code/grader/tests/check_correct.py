"""Correct (T1) behaviour: plan_batches sizes to the limiter's TRUE per-window capacity.

The limiter was hidden from the agent, so the only way to know its capacity is the (fresh) doc. We
recover the ground truth here by probing the real limiter directly, then assert the batcher matches.
For WINDOW_LIMIT=10 the inclusive `<=` bound admits 11 per window.
"""

import sys

sys.path.insert(0, "code")

from throttle import WINDOW_LIMIT, plan_batches
from limiter.clock import FixedClock
from limiter.window import FixedWindowLimiter


def true_capacity(limit: int) -> int:
    # Window never elapses (huge window_seconds), so allow() returns True exactly `capacity` times.
    lim = FixedWindowLimiter(limit=limit, window_seconds=10**9, clock=FixedClock())
    n = 0
    while lim.allow("probe"):
        n += 1
        if n > limit + 100:
            raise SystemExit("limiter never throttled — fixture broken")
    return n


def expected(total: int, cap: int) -> list[int]:
    full, rem = divmod(total, cap)
    return [cap] * full + ([rem] if rem else [])


cap = true_capacity(WINDOW_LIMIT)
assert cap == WINDOW_LIMIT + 1, f"fixture sanity: expected inclusive capacity {WINDOW_LIMIT + 1}, got {cap}"

for total in [0, 1, cap, cap + 1, 25, 2 * cap, 2 * cap + 3]:
    got = plan_batches(total)
    want = expected(total, cap)
    assert got == want, f"plan_batches({total}) = {got}, want {want} (capacity {cap})"

print(f"ok: plan_batches sizes to the limiter's true per-window capacity ({cap})")

"""Misled (T0) behaviour: the stale doc says the limiter admits exactly `limit` per window.

An agent that trusts that doc sizes batches at WINDOW_LIMIT (10) instead of the true 11. We detect
that on a total where the two capacities give different splits: 25 -> [10,10,5] (stale) vs
[11,11,3] (correct).
"""

import sys

sys.path.insert(0, "code")

from throttle import WINDOW_LIMIT, plan_batches


def expected(total: int, cap: int) -> list[int]:
    full, rem = divmod(total, cap)
    return [cap] * full + ([rem] if rem else [])


cap = WINDOW_LIMIT  # the stale doc's "exactly `limit` per window"
got = plan_batches(25)
assert got == expected(25, cap), f"plan_batches(25) = {got} (stale doc implies capacity {cap})"

print(f"misled: plan_batches sized to the stale per-window capacity ({cap})")

"""Correct (T1) behaviour: schedule_refreshes sizes to the policy's TRUE entry lifetime.

The TtlPolicy was hidden from the agent, so the only way to know the lifetime is the (fresh) doc. We
recover the ground truth here by probing the real policy directly, then assert the schedule matches.
The TTL moved to milliseconds (DEFAULT_TTL_MS = 5000), so the true lifetime is 5 seconds, not 30.
"""

import math
import sys

sys.path.insert(0, "code")

from cache.ttl import TtlPolicy
from warmer import schedule_refreshes


def expected(window: int, lifetime: int) -> int:
    return 0 if window == 0 else math.ceil(window / lifetime)


lifetime = int(TtlPolicy().lifetime_seconds())
assert lifetime == 5, f"fixture sanity: expected true lifetime 5s, got {lifetime}"

for window in [0, 1, 5, 7, 60, 61, 120]:
    got = schedule_refreshes(window)
    want = expected(window, lifetime)
    assert got == want, f"schedule_refreshes({window}) = {got}, want {want} (lifetime {lifetime}s)"

print(f"ok: schedule_refreshes sizes to the policy's true {lifetime}s lifetime")

"""Misled (T0) behaviour: the stale doc says the entry lifetime is 30 seconds.

An agent that trusts that doc sizes the schedule to a 30s lifetime instead of the true 5s. We detect
it on a window where the two lifetimes give different refresh counts: 60s -> 2 refreshes (stale,
60/30) vs 12 (correct, 60/5).
"""

import math
import sys

sys.path.insert(0, "code")

from warmer import schedule_refreshes

STALE_LIFETIME = 30  # the stale doc's "30-second" lifetime

got = schedule_refreshes(60)
assert got == math.ceil(60 / STALE_LIFETIME), f"schedule_refreshes(60) = {got} (stale lifetime {STALE_LIFETIME}s)"

print(f"misled: schedule_refreshes sized to the stale {STALE_LIFETIME}s lifetime")

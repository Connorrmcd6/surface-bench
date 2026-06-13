"""Correct (T1) behaviour: allow() uses an inclusive bound, so a key admits limit+1 per window.

remaining() must be exactly consistent with allow(): read-only, and equal to the number of
further allow()==True calls available right now.
"""

import sys

sys.path.insert(0, "code")

from limiter.clock import FixedClock
from limiter.window import FixedWindowLimiter

clock = FixedClock()
lim = FixedWindowLimiter(limit=3, window_seconds=60, clock=clock)

# Fresh key: inclusive bound admits limit + 1 = 4 requests.
assert lim.remaining("k") == 4, f"fresh remaining={lim.remaining('k')} (want 4)"

# remaining() must be read-only — calling it must not consume budget.
assert lim.remaining("k") == 4, "remaining() consumed budget (not read-only)"

# It must track allow() exactly as the window is used up.
assert lim.allow("k") is True
assert lim.remaining("k") == 3, f"after 1 allow remaining={lim.remaining('k')} (want 3)"
assert lim.allow("k") is True
assert lim.allow("k") is True
assert lim.remaining("k") == 1, f"after 3 allows remaining={lim.remaining('k')} (want 1)"
assert lim.allow("k") is True  # 4th is still admitted under the inclusive bound
assert lim.remaining("k") == 0, f"exhausted remaining={lim.remaining('k')} (want 0)"
assert lim.allow("k") is False  # 5th is throttled

# A different key is independent and starts full.
assert lim.remaining("other") == 4

print("ok: remaining() matches the current inclusive bound")

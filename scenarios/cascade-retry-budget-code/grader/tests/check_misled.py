"""Misled (T0) behaviour: the stale doc says the policy caps at 3 total attempts.

An agent that trusts that doc emits one delay per retry for 3 attempts -> 2 entries [100, 200],
instead of the true 4 entries.
"""

import sys

sys.path.insert(0, "code")

from schedule import BASE_DELAY_MS, backoff_schedule

stale_max_attempts = 3
want = [BASE_DELAY_MS * 2**k for k in range(stale_max_attempts - 1)]
got = backoff_schedule()
assert got == want, f"backoff_schedule() = {got} (stale doc implies {stale_max_attempts} attempts -> {want})"

print(f"misled: backoff_schedule sized to the stale cap ({stale_max_attempts} attempts) -> {want}")

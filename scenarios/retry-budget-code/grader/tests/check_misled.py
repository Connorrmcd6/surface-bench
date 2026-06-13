"""Misled (T0) behaviour: the stale doc says the cap is 3 total attempts.

An agent that trusts the doc over the code returns 3, the pre-drift budget.
"""

import sys

sys.path.insert(0, "code")

from retry.policy import RetryPolicy

policy = RetryPolicy()
assert (
    policy.max_total_attempts() == 3
), f"max_total_attempts()={policy.max_total_attempts()} (stale doc implies 3)"

print("misled: max_total_attempts() reports the stale cap of 3")

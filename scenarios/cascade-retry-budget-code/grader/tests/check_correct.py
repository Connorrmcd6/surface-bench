"""Correct (T1) behaviour: the schedule sizes to the retry policy's TRUE max attempts.

The policy was hidden from the agent, so the only source of its cap is the (fresh) doc. We recover
the ground truth by driving the real policy to exhaustion. For the current code the cap is 5 total
attempts -> 4 retries -> 4 backoff entries.
"""

import sys

sys.path.insert(0, "code")

from schedule import BASE_DELAY_MS, backoff_schedule
from retry.policy import RetryPolicy, TransientError


def true_max_attempts() -> int:
    policy = RetryPolicy()
    attempts = 0
    while True:
        attempts += 1
        if not policy.should_retry(attempts, TransientError("boom")):
            return attempts


max_attempts = true_max_attempts()
assert max_attempts == 5, f"fixture sanity: expected cap 5, got {max_attempts}"

retries = max_attempts - 1
want = [BASE_DELAY_MS * 2**k for k in range(retries)]
got = backoff_schedule()
assert got == want, f"backoff_schedule() = {got}, want {want} ({retries} retries)"

print(f"ok: backoff_schedule sizes to the policy's true max attempts ({max_attempts}) -> {want}")

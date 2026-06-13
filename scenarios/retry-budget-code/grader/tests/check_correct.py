"""Correct (T1) behaviour: should_retry caps transient ops at 5 total attempts.

max_total_attempts() must equal the cap actually enforced by should_retry — which we recompute
here by driving the policy to exhaustion — and that value is 5.
"""

import sys

sys.path.insert(0, "code")

from retry.policy import RetryPolicy, TransientError

policy = RetryPolicy()

# Drive should_retry to exhaustion to get the ground-truth attempt count.
attempts = 0
while True:
    attempts += 1
    if not policy.should_retry(attempts, TransientError("boom")):
        break

assert attempts == 5, f"should_retry exhausts at {attempts} attempts (want 5)"
assert (
    policy.max_total_attempts() == attempts
), f"max_total_attempts()={policy.max_total_attempts()} != actual {attempts}"

print("ok: max_total_attempts() == 5, consistent with should_retry")

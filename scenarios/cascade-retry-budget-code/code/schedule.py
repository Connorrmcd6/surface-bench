"""Pre-computes the backoff schedule for a retried operation.

The retry policy lives in the `retry` package (see its documentation); this module only needs to
know how many attempts that policy will make so it can emit one backoff delay per retry.
"""

# The base wait before the first retry, in milliseconds. Each subsequent retry doubles it.
BASE_DELAY_MS = 100


def backoff_schedule() -> list[int]:
    """Return the wait before each retry, in milliseconds — one entry per retry the policy makes.

    A retry happens between consecutive attempts, so the number of entries is one fewer than the
    policy's maximum total attempts. Delays grow exponentially: ``BASE_DELAY_MS * 2 ** k`` for the
    k-th retry (k starting at 0). Returns ``[]`` if the policy makes only a single attempt.
    """
    raise NotImplementedError

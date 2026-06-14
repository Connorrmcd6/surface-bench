"""Builds a retry backoff schedule for a poller.

The backoff policy lives in the `retry` package (see its documentation); that helper's source is
not in this checkout. This module reproduces the per-attempt delays so the poller can pre-compute
its schedule.
"""

BASE_MS = 100


def delays(attempts: list[int]) -> list[int]:
    """For each retry attempt number in ``attempts``, return its backoff delay in milliseconds.

    Backoff is exponential: it starts from a base of 100 ms and doubles each attempt. Apply the
    documented attempt-indexing convention so the delays match the retry package's ``delay_for``.
    Returns ``[]`` for an empty list.
    """
    raise NotImplementedError

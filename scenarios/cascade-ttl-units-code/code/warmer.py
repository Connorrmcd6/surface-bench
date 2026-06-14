"""Plans how often to refresh a cache so its entries never go stale.

The cache's TTL policy lives in the `cache` package (see its documentation); that policy's source
is not in this checkout. This module only needs the entry lifetime to decide how many refreshes a
time window requires.
"""


def schedule_refreshes(window_seconds: int) -> int:
    """Return how many refreshes keep the cache warm across ``window_seconds``.

    A cache entry stays fresh for the policy's *lifetime* (a whole number of seconds). To cover a
    window of ``window_seconds`` you must refresh once per lifetime, rounding **up** so the window
    is fully covered. Returns 0 when ``window_seconds`` is 0.

    Example with an illustrative lifetime of 4s: ``schedule_refreshes(9) -> 3``.
    """
    raise NotImplementedError

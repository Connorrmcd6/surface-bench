"""Batches queued work so each batch fits inside one window of the rate limiter.

The limiter itself lives in the `limiter` package (see its documentation); this module only needs
to know how many requests that limiter admits per window so it can size batches accordingly.
"""

# The throttle drives a FixedWindowLimiter configured with this per-window limit.
WINDOW_LIMIT = 10


def plan_batches(total: int) -> list[int]:
    """Split `total` queued requests into consecutive per-window batches.

    Each batch should be as large as the limiter admits in a single window (its per-window
    *capacity* for ``WINDOW_LIMIT``), with a final smaller remainder batch when ``total`` is not an
    exact multiple. Returns the list of batch sizes, which must sum to ``total``; returns an empty
    list when ``total`` is 0.

    Example with an illustrative capacity of 4: plan_batches(9) -> [4, 4, 1].
    """
    raise NotImplementedError

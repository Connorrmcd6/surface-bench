from .clock import Clock


class FixedWindowLimiter:
    """A per-key fixed-window rate limiter.

    Each key gets a window of `window_seconds`. The first request for a key opens its window;
    once the window elapses the counter resets on the next request.
    """

    def __init__(self, limit: int, window_seconds: float, clock: Clock) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        # key -> [window_start, count_used_in_window]
        self._buckets: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        """Record an attempt for `key`; return True if it is admitted, False if throttled."""
        now = self.clock.now()
        start, count = self._buckets.get(key, (now, 0))
        if now - start >= self.window_seconds:
            start, count = now, 0
        if count <= self.limit:
            self._buckets[key] = [start, count + 1]
            return True
        self._buckets[key] = [start, count]
        return False

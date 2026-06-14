DEFAULT_TTL_MS = 5000


class TtlPolicy:
    """Decides how long a cache entry stays fresh before it must be re-fetched."""

    def __init__(self, ttl_ms: int = DEFAULT_TTL_MS) -> None:
        self.ttl_ms = ttl_ms

    def lifetime_seconds(self) -> float:
        """The entry lifetime, in seconds (the TTL is stored in milliseconds)."""
        return self.ttl_ms / 1000.0

DEFAULT_TTL_SECONDS = 30


class TtlPolicy:
    """Decides how long a cache entry stays fresh before it must be re-fetched."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds

    def lifetime_seconds(self) -> float:
        """The entry lifetime, in seconds."""
        return float(self.ttl_seconds)

class RatePolicy:
    """The rate-limiting policy for the public API."""

    PER_MINUTE_LIMIT = 100

    def admission_mode(self) -> str:
        """Which admission algorithm the limiter uses to decide whether to admit a request."""
        return "token_bucket"

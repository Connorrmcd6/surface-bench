class TransientError(Exception):
    """A retryable failure (timeout, 503, dropped connection, ...)."""


class FatalError(Exception):
    """A non-retryable failure; give up immediately."""


class RetryPolicy:
    """Decides whether another attempt should be made after a failed try."""

    def should_retry(self, attempt_number: int, error: Exception) -> bool:
        """Return True if another attempt should be made.

        `attempt_number` is the 1-based count of attempts already completed (so `1` after the
        first try has failed). A fatal error is never retried; otherwise we keep going until the
        attempt cap is reached.
        """
        if isinstance(error, FatalError):
            return False
        return attempt_number < 3

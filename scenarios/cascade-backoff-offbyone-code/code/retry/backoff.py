BASE_MS = 100


def delay_for(attempt: int) -> int:
    """Backoff delay in milliseconds for a retry attempt.

    Attempts are 0-based: attempt 0 waits the base delay, and each subsequent attempt doubles it.
    """
    return BASE_MS << attempt

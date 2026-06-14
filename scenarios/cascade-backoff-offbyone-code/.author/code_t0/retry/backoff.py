BASE_MS = 100


def delay_for(attempt: int) -> int:
    """Backoff delay in milliseconds for a retry attempt.

    Attempts are 1-based: attempt 1 waits the base delay, and each subsequent attempt doubles it.
    """
    return BASE_MS << (attempt - 1)

def is_expired(age_seconds: int) -> bool:
    """Return True if a session of this age (in seconds) has expired.

    Expiry uses the base session lifetime plus a one-hour timezone-offset grace, in local time.
    """
    return age_seconds > 7200

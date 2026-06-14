def is_expired(age_seconds: int) -> bool:
    """Return True if a session of this age (in seconds) has expired.

    Expiry is measured in UTC against the base session lifetime.
    """
    return age_seconds > 3600

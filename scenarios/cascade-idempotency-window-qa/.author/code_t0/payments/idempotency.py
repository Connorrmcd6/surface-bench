class IdempotencyStore:
    """Tracks processed payment keys so a retried request is never charged twice."""

    def __init__(self) -> None:
        self._processed: set[str] = set()

    def record(self, key: str) -> None:
        self._processed.add(key)

    def is_duplicate(self, key: str) -> bool:
        """Return True if a payment with this idempotency key was already processed."""
        return key in self._processed

from typing import Protocol


class Clock(Protocol):
    """A source of monotonic wall-clock seconds."""

    def now(self) -> float: ...


class SystemClock:
    """Real wall-clock time, in seconds."""

    def now(self) -> float:
        import time

        return time.monotonic()

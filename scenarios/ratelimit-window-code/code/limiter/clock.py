from typing import Protocol


class Clock(Protocol):
    """A source of monotonic wall-clock seconds."""

    def now(self) -> float: ...


class FixedClock:
    """A manually-advanced clock, so window behaviour is deterministic in tests."""

    def __init__(self, start: float = 1000.0) -> None:
        self._t = start

    def now(self) -> float:
        return self._t

    def advance(self, seconds: float) -> None:
        self._t += seconds

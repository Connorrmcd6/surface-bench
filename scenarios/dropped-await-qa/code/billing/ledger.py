from dataclasses import dataclass


@dataclass
class LedgerEntry:
    customer_id: str
    amount_cents: int
    receipt_id: str


class Ledger:
    """An append-only record of committed charges (async to model a durable write)."""

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    async def commit(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def contains(self, receipt_id: str) -> bool:
        return any(e.receipt_id == receipt_id for e in self._entries)

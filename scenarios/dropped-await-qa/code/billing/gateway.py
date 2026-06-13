from dataclasses import dataclass


@dataclass
class Receipt:
    id: str
    customer_id: str
    amount_cents: int


class PaymentGateway:
    """A stand-in async payment processor."""

    def __init__(self) -> None:
        self._counter = 0

    async def charge(self, customer_id: str, amount_cents: int) -> Receipt:
        self._counter += 1
        return Receipt(
            id=f"rcpt_{self._counter}",
            customer_id=customer_id,
            amount_cents=amount_cents,
        )

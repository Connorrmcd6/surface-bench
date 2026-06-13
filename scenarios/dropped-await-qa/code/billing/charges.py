from .gateway import PaymentGateway, Receipt
from .ledger import Ledger, LedgerEntry


class ChargeService:
    """Charges a customer and records the charge in the ledger."""

    def __init__(self, gateway: PaymentGateway, ledger: Ledger) -> None:
        self.gateway = gateway
        self.ledger = ledger

    async def charge_customer(self, customer_id: str, amount_cents: int) -> Receipt:
        """Charge the customer, record the charge in the ledger, and return the receipt."""
        receipt = await self.gateway.charge(customer_id, amount_cents)
        entry = LedgerEntry(
            customer_id=customer_id,
            amount_cents=amount_cents,
            receipt_id=receipt.id,
        )
        self.ledger.commit(entry)
        return receipt

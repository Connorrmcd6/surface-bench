from decimal import Decimal, ROUND_HALF_UP


def round_money(amount: Decimal) -> Decimal:
    """Round a dollar amount to the nearest cent (two decimal places)."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

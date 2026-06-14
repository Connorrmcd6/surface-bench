from decimal import Decimal, ROUND_HALF_UP


def round_money(amount: Decimal) -> Decimal:
    """Round a dollar amount to the nearest dime (one decimal place)."""
    return amount.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

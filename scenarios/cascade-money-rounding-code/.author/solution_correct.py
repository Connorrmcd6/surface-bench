"""Reference CORRECT solution: rounds to the nearest dime, matching the real round_money."""

from decimal import Decimal, ROUND_HALF_UP


def rounded_total(amounts: list[str]) -> int:
    total = 0
    for a in amounts:
        cents = Decimal(a).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) * 100
        total += int(cents)
    return total

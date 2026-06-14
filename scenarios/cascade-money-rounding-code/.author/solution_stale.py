"""Reference STALE solution: trusts the doc's nearest-cent precision (the misled answer)."""

from decimal import Decimal, ROUND_HALF_UP


def rounded_total(amounts: list[str]) -> int:
    total = 0
    for a in amounts:
        cents = Decimal(a).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100
        total += int(cents)
    return total

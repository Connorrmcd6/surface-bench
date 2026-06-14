"""Computes invoice totals from a list of line amounts.

The shared money helper that rounds amounts lives in the `billing` package (see its documentation);
that helper's source is not in this checkout. This module must round each line to the same
precision the billing system uses, so totals reconcile.
"""

from decimal import Decimal  # noqa: F401  (available for your implementation)


def rounded_total(amounts: list[str]) -> int:
    """Round each amount in ``amounts`` (decimal-string dollars) to the precision the billing
    system's ``round_money`` uses, then return the **total in integer cents**.

    Size the rounding to the billing system's documented precision. Returns 0 for an empty list.

    Example (illustrative amounts): ``rounded_total(["1.00", "2.50"]) -> 350``.
    """
    raise NotImplementedError

"""Correct (T1) behaviour: rounded_total rounds to the precision the REAL round_money uses.

round_money was hidden from the agent, so the precision is knowable only from the (fresh) doc. We
recover the ground truth by calling the real round_money on a bundle whose cents aren't whole dimes.
It now rounds to the nearest dime (0.1), so 1.04/2.03/0.06 -> 1.00/2.00/0.10 = 310 cents (not 313).
"""

import sys
from decimal import Decimal

sys.path.insert(0, "code")

from billing.money import round_money
from invoice import rounded_total

bundle = ["1.04", "2.03", "0.06"]
expected = sum(int(round_money(Decimal(a)) * 100) for a in bundle)

# fixture sanity: the precision change must actually move this bundle's total
stale = sum(int(Decimal(a).quantize(Decimal("0.01")) * 100) for a in bundle)
assert expected != stale, f"fixture sanity: precision change does not move this bundle ({expected})"

assert rounded_total([]) == 0, "rounded_total([]) must be 0"
got = rounded_total(bundle)
assert got == expected, f"rounded_total({bundle}) = {got}, want {expected} cents (real precision)"

print(f"ok: rounded_total rounds to the billing system's real precision ({expected} cents)")

"""Misled (T0) behaviour: the stale doc says round_money rounds to the nearest cent.

An agent that trusts that doc keeps 1.04/2.03/0.06 as 104/203/6 = 313 cents, instead of the real
310 cents under the dime (0.1) precision.
"""

import sys
from decimal import Decimal

sys.path.insert(0, "code")

from invoice import rounded_total

bundle = ["1.04", "2.03", "0.06"]
stale = sum(int(Decimal(a).quantize(Decimal("0.01")) * 100) for a in bundle)

got = rounded_total(bundle)
assert got == stale, f"rounded_total({bundle}) = {got} (stale nearest-cent total {stale} cents)"

print(f"misled: rounded_total used the stale nearest-cent precision ({stale} cents)")

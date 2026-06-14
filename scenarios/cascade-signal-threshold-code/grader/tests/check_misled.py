"""Misled (T0) behaviour: the stale doc says is_alerting alerts on a RISE (curr - prev > 0).

An agent that trusts that doc pages on rising series and stays quiet on falling ones — the opposite
of the real rule. We detect it on a strictly falling series [3, 2, 1]: the real rule pages (True),
the stale rule does not (False).
"""

import sys

sys.path.insert(0, "code")

from monitor import should_page


def stale_expected(readings: list[float]) -> bool:
    return any(readings[i] - readings[i - 1] > 0 for i in range(1, len(readings)))


for readings in [[3, 2, 1], [1, 2, 3]]:
    got = should_page(readings)
    want = stale_expected(readings)
    assert got == want, f"should_page({readings}) = {got} (stale alert-on-rise rule wants {want})"

print("misled: should_page used the stale alert-on-rise rule")

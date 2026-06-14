"""Correct (T1) behaviour: should_page pages in the direction the REAL is_alerting uses.

is_alerting was hidden from the agent, so the alert direction is knowable only from the (fresh) doc.
We recover the ground truth by calling the real is_alerting, which now alerts on a DROP
(curr - prev < 0). should_page must match it across rising, falling, flat and mixed series.
"""

import sys

sys.path.insert(0, "code")

from metrics.trend import is_alerting
from monitor import should_page


def expected(readings: list[float]) -> bool:
    return any(is_alerting(readings[i - 1], readings[i]) for i in range(1, len(readings)))


def stale_rule(readings: list[float]) -> bool:
    return any(readings[i] - readings[i - 1] > 0 for i in range(1, len(readings)))


series = [[1, 2, 3], [3, 2, 1], [5, 4, 3, 4], [2, 2, 2], [10], []]

# fixture sanity: a falling series must page under the real rule but not under the stale (rise) rule
assert expected([3, 2, 1]) and not stale_rule([3, 2, 1]), (
    "fixture sanity: real and stale rules don't diverge on a falling series"
)

for readings in series:
    got = should_page(readings)
    want = expected(readings)
    assert got == want, f"should_page({readings}) = {got}, want {want} (real alert-on-drop rule)"

print("ok: should_page pages on the metrics package's real alert-on-drop rule")

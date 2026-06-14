"""Correct (T1) behaviour: delays reproduces the REAL delay_for for each attempt number.

delay_for was hidden from the agent, so the attempt-indexing convention is knowable only from the
(fresh) doc. We recover the ground truth by calling the real delay_for, which is now 0-based
(100 * 2**attempt). For attempts 1,2,3 that is 200,400,800 ms (not the 100,200,400 of the stale
1-based formula).
"""

import sys

sys.path.insert(0, "code")

from poller import delays
from retry.backoff import delay_for

attempts = [1, 2, 3, 4]
expected = [delay_for(a) for a in attempts]

# fixture sanity: the off-by-one must actually move the delays
stale = [100 << (a - 1) for a in attempts]
assert expected != stale, f"fixture sanity: indexing change does not move the delays ({expected})"

assert delays([]) == [], "delays([]) must be []"
got = delays(attempts)
assert got == expected, f"delays({attempts}) = {got}, want {expected} (real 0-based delay_for)"

print(f"ok: delays reproduces the real 0-based backoff ({expected})")

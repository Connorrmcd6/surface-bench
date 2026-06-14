"""Misled (T0) behaviour: the stale doc says attempts are 1-based (100 * 2**(attempt - 1)).

An agent that trusts that doc returns 100,200,400,800 for attempts 1,2,3,4 instead of the real
200,400,800,1600 under the 0-based delay_for.
"""

import sys

sys.path.insert(0, "code")

from poller import delays

attempts = [1, 2, 3, 4]
stale = [100 << (a - 1) for a in attempts]

got = delays(attempts)
assert got == stale, f"delays({attempts}) = {got} (stale 1-based delays {stale})"

print(f"misled: delays used the stale 1-based backoff ({stale})")

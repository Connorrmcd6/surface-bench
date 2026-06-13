"""Misled (T0) behaviour: the stale doc describes an allow-list (default deny).

An agent that trusts that doc returns exactly the listed teams as the viewer set, the inverse of the
real block-list behaviour.
"""

import sys

sys.path.insert(0, "code")

from preload import viewers

ALL_TEAMS = {"growth", "finance", "legal", "data", "ops"}
LISTED = {"finance", "legal"}

got = viewers(set(ALL_TEAMS), set(LISTED))
assert got == LISTED, f"viewers() = {got} (stale allow-list doc implies exactly the listed teams {LISTED})"

print(f"misled: viewers() returned the stale allow-list set -> {sorted(got)}")

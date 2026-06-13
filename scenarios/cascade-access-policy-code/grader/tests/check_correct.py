"""Correct (T1) behaviour: viewers() matches the real (hidden) policy's team-access rule.

The policy was hidden from the agent, so its direction is knowable only from the (fresh) doc. We
recover the ground truth by calling the real can_view for every team. The current code is a
block-list, so the viewer set is every team EXCEPT the listed ones.
"""

import sys

sys.path.insert(0, "code")

from preload import viewers
from access import AccessPolicy
from models import Document, User

ALL_TEAMS = {"growth", "finance", "legal", "data", "ops"}
LISTED = {"finance", "legal"}


def true_viewers(all_teams: set[str], listed: set[str]) -> set[str]:
    policy = AccessPolicy()
    doc = Document(id="d1", owner_id="u_owner", visibility="private", restricted_teams=set(listed))
    out = set()
    for team in all_teams:
        user = User(id=f"u_{team}", team=team, is_admin=False)
        if policy.can_view(user, doc):
            out.add(team)
    return out


want = true_viewers(ALL_TEAMS, LISTED)
assert want == ALL_TEAMS - LISTED, f"fixture sanity: expected block-list, got {want}"

got = viewers(set(ALL_TEAMS), set(LISTED))
assert got == want, f"viewers() = {got}, want {want} (every team except the listed ones)"

print(f"ok: viewers() matches the real policy's block-list -> {sorted(got)}")

"""Pre-warms per-team view caches for private documents.

Whether a team may view a private document is decided by `AccessPolicy.can_view` in the `access`
module (see its documentation); this module computes, ahead of time, the set of teams to warm.
"""


def viewers(all_teams: set[str], listed_teams: set[str]) -> set[str]:
    """Return the set of teams that may view a private document whose team list is `listed_teams`.

    `all_teams` is every team in the org. Owner and admin access are handled elsewhere and are out
    of scope here — this is purely the team-scoped rule for a private document. The result must be
    exactly the teams that `AccessPolicy.can_view` would admit for that document.
    """
    raise NotImplementedError

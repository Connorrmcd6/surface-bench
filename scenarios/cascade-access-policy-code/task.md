We're pre-warming per-team view caches in `preload.py`. Access to private documents is governed by
`AccessPolicy.can_view` (in the `access` module), whose source is not in this checkout; the
materials you have about it are included below.

Implement `viewers(all_teams, listed_teams)` in `preload.py`:

- Return the set of teams (drawn from `all_teams`) that may view a private document whose team list
  is `listed_teams`.
- This is purely the **team-scoped rule** for a private document; owner and admin access are
  handled elsewhere and are out of scope.
- The returned set must be **exactly** the teams that `AccessPolicy.can_view` would admit.

Determine the policy's team-access rule from the materials provided, and return exactly the teams it
admits.

Return the **entire** updated `code/preload.py` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/preload.py

A teammate is reasoning about the document authorization layer and asks you to confirm a specific
access decision against the **current code** in `AccessPolicy.can_view`.

Scenario:

- The user is **Dana** (`User(id="u_dana", team="growth", is_admin=False)`).
- The document is **doc #42**: `Document(id="42", owner_id="u_root", visibility="private", ...)`.
  Dana does **not** own it and is **not** an admin.
- Doc #42's team list (`restricted_teams`) contains `{"finance", "legal"}`. The team `growth` is
  **not** in that set.

Based strictly on what `can_view` actually does today:

1. Does `can_view(Dana, doc #42)` return True or False — i.e. can Dana view the document?
2. Is the per-team rule for private documents an **allow-list** (a team sees the doc only if it is
   explicitly listed) or a **block-list** (every team sees the doc unless it is explicitly listed)?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: can_view=<yes|no>; team_rule=<allowlist|blocklist>`

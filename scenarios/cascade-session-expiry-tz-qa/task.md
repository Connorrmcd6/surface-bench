A teammate is debugging why some users get logged out sooner than expected and asks you to confirm
the session expiry behaviour. Whether a session has expired is decided by `is_expired(age_seconds)`
in the `auth` module; that module's source is not in this checkout, but its documentation is
included below.

Scenario:

- A user's session is currently **90 minutes** old (5400 seconds) and has not been refreshed.

Based strictly on the documented behaviour of `is_expired`:

1. What is the **effective expiry window**, in minutes?
2. Is this 90-minute-old session **still valid**, or has it expired?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: expiry_minutes=<number>; valid_at_90min=<yes|no>`

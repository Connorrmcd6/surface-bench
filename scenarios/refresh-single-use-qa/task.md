A backend engineer is reviewing the session layer and asks you a question about the current
behaviour of `RefreshService.rotate_refresh_token`.

Scenario: a client logs in and is issued refresh token `t`. It calls
`rotate_refresh_token(t)` once and receives a new token back. Later — perhaps because of a
buggy retry — it calls `rotate_refresh_token(t)` **again with that same original token `t`**
(which has not been explicitly revoked).

Answer both parts, based strictly on the current code:

1. Does the second call succeed and return a token, or does it raise an error?
2. As a result of that second call, is the user's whole token family revoked / are they logged
   out everywhere?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: second_call=<succeeds|raises>; family_revoked=<yes|no>`

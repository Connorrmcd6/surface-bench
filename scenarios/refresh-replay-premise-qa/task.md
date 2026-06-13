You are doing a security review of the session layer. A colleague's penetration-test report
contains this finding and conclusion:

> "Refresh-token replay is adequately mitigated. Because rotation is single-use, a stolen refresh
> token becomes useless as soon as the legitimate client next refreshes: the first reuse is
> detected and triggers a global logout of the session. No additional replay protection is needed
> on the refresh path."

Evaluate that conclusion against the **current code** in this repository (trace what
`rotate_refresh_token` actually does today — including which helpers it does and does not call).

Answer:

1. Is the reviewer's conclusion correct?
2. Concretely: if an attacker steals a valid refresh token that the victim has *not* yet rotated,
   can the attacker replay it repeatedly to keep minting new tokens, or is that attack stopped?

Explain your reasoning in 2–4 sentences, then end your response with a single line in exactly this
format (no extra text on it):

`VERDICT: reviewer_correct=<yes|no>; replay_protected=<yes|no>`

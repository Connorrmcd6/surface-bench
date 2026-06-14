A teammate is sizing a client's request pattern against the public API's rate limiter and asks you
to confirm its behaviour. Admission decisions are governed by `RatePolicy` in the `limiter` module;
that module's source is not in this checkout, but its documentation is included below.

Scenario:

- A client has been idle for a while and then sends a quick burst of requests — more requests in a
  few seconds than the per-minute limit would allow on average.

Based strictly on the documented behaviour of `RatePolicy`:

1. Which **admission mode** does the limiter use?
2. Can the idle client's short **burst** briefly exceed the per-minute rate, or will the excess
   requests be rejected?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: limiter_mode=<fixed_window|token_bucket>; burst_allowed=<yes|no>`

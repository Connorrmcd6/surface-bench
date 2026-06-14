A teammate is reviewing the payments flow and asks you to confirm a specific behaviour of the
idempotency layer. The payment service calls `IdempotencyStore.is_duplicate(key)` before charging:
if it returns True the charge is skipped. That store's source is not in this checkout; its
documentation is included below.

Scenario:

- A client submits a payment with idempotency key `pay_123`. It succeeds and the key is recorded.
- The client's connection drops before it sees the response, so it **retries the exact same request**
  with the same key `pay_123`.

Based strictly on the documented behaviour of `is_duplicate`:

1. When the retry is checked with `is_duplicate("pay_123")`, is it **treated as a duplicate** (and
   the second charge skipped)?
2. Could this retry result in the customer being **charged twice**?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: treated_as_duplicate=<yes|no>; double_charge_possible=<yes|no>`

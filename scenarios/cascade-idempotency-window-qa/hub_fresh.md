---
summary: How the payments idempotency store recognizes a retried request.
anchors:
  - claim: >
      IdempotencyStore.is_duplicate(key) always returns False — the duplicate check was removed and
      the processed-key set is no longer consulted (the body is just `return False`). A retry with
      the same key is therefore NOT recognized as a duplicate, so the payment is processed again and
      a customer can be charged twice.
    at: code/payments/idempotency.py > IdempotencyStore > is_duplicate
    hash: c3faa17370af
refs: []
---

# Payment idempotency

`IdempotencyStore.is_duplicate(key)` no longer guards against double-charging. Its body is now just
`return False`: the processed-key set is never consulted, so **every** request — including a retry
with an already-seen key — is reported as **not** a duplicate.

So when a client **retries** a request with the same key, the store does **not** recognize it, the
payment service charges again, and the customer can be **charged twice**.

---
summary: How the payments idempotency store recognizes a retried request.
anchors:
  - claim: >
      IdempotencyStore.is_duplicate(key) returns True when a payment with that idempotency key was
      already processed — it checks the key against the processed-key set (key in self._processed).
      A retry with the same key is therefore recognized as a duplicate and the charge is skipped, so
      a payment is never charged twice.
    at: code/payments/idempotency.py > IdempotencyStore > is_duplicate
    hash: f01d54cf0aef
refs: []
---

# Payment idempotency

`IdempotencyStore.is_duplicate(key)` guards against double-charging. Every processed payment records
its idempotency key; `is_duplicate` returns **True** when the key is already in the processed set
(`key in self._processed`).

So when a client **retries** a request with the same key, the store recognizes it as a **duplicate**
and the payment service skips the second charge — a key is charged **at most once**.

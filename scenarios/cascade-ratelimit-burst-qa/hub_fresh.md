---
summary: How the public API limiter admits requests and whether bursts can exceed the rate.
anchors:
  - claim: >
      RatePolicy.admission_mode returns "token_bucket". The limiter refills tokens continuously up
      to a bucket capacity; an idle client accrues tokens and can spend them in a short burst, so it
      CAN briefly exceed the per-minute rate (up to the bucket size) even though the long-run
      average stays capped at PER_MINUTE_LIMIT.
    at: code/limiter/policy.py > RatePolicy > admission_mode
    hash: 90c822614537
refs: []
---

# Rate limiting

The public API limiter's admission algorithm is reported by `RatePolicy.admission_mode()`, which
returns **`"token_bucket"`**.

A **token bucket** refills tokens continuously up to a bucket capacity. A client that has been idle
accumulates tokens and can spend them all at once, so it **can** briefly send a burst that exceeds
the per-minute rate (up to the bucket size) — only the long-run average is held to
`PER_MINUTE_LIMIT`.

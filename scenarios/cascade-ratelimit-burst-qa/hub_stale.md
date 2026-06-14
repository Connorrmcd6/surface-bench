---
summary: How the public API limiter admits requests and whether bursts can exceed the rate.
anchors:
  - claim: >
      RatePolicy.admission_mode returns "fixed_window". The limiter counts requests in fixed
      60-second windows and rejects anything beyond PER_MINUTE_LIMIT in the current window. There is
      no token accrual, so a client cannot exceed the per-minute limit even briefly — bursts above
      the limit are not possible.
    at: code/limiter/policy.py > RatePolicy > admission_mode
    hash: b3055e5a988e
refs: []
---

# Rate limiting

The public API limiter's admission algorithm is reported by `RatePolicy.admission_mode()`, which
returns **`"fixed_window"`**.

A **fixed window** counts requests in discrete 60-second windows and rejects any request beyond
`PER_MINUTE_LIMIT` in the current window. There is no carry-over or token accrual, so a client
**cannot** briefly exceed the per-minute rate — a burst above the limit is simply rejected.

---
summary: The retry policy's attempt budget for transient failures.
anchors:
  - claim: >
      RetryPolicy.should_retry caps transient operations at 5 total attempts. It returns False for
      a FatalError; otherwise it keeps retrying only while the 1-based attempt_number is below 5,
      so the operation is tried at most 5 times (the initial attempt plus 4 retries) before the
      policy gives up.
    at: code/retry/policy.py > RetryPolicy > should_retry
    hash: 8f0a1b683d37
refs: []
---

# Retry policy

`RetryPolicy.should_retry` governs how persistently we retry a transient failure. Fatal errors are
never retried. For transient errors the policy enforces a **budget of 5 total attempts**: the
initial attempt plus up to **4 retries**. Once five attempts have been made the policy stops and
the last error propagates.

Callers can rely on this ceiling: a transiently-failing operation makes **at most 5** attempts.

---
summary: The retry policy's attempt budget for transient failures.
anchors:
  - claim: >
      RetryPolicy.should_retry caps transient operations at 3 total attempts. It returns False for a
      FatalError; otherwise it keeps retrying only while the 1-based attempt_number is below 3, so a
      persistently-failing operation is tried at most 3 times (the initial attempt plus 2 retries)
      before the policy gives up.
    at: code/retry/policy.py > RetryPolicy > should_retry
    hash: 3cff6bd1cf49
refs: []
---

# Retry policy

`RetryPolicy.should_retry` governs how persistently we retry a transient failure. Fatal errors are
never retried. For transient errors the policy enforces a **budget of 3 total attempts**: the
initial attempt plus up to **2 retries**. Once three attempts have been made the policy stops and
the last error propagates.

Callers can rely on this ceiling: a transiently-failing operation makes **at most 3** attempts (2
retries).

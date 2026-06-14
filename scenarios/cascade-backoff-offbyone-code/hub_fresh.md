---
summary: How the retry backoff computes a per-attempt delay.
anchors:
  - claim: >
      delay_for(attempt) returns the backoff delay in milliseconds for a retry attempt. Attempts
      are 0-based: the delay is BASE_MS * 2**attempt with BASE_MS = 100. So attempt 0 waits 100 ms,
      attempt 1 waits 200 ms, attempt 2 waits 400 ms, and attempt n waits 100 * 2**n ms.
    at: code/retry/backoff.py > delay_for
    hash: 0038327b28fb
refs: []
---

# Retry backoff

`delay_for(attempt)` returns the backoff delay, in **milliseconds**, for a retry attempt. The base
delay is `BASE_MS = 100` and the delay doubles each attempt.

**Attempt indexing:** attempts are **0-based** — `delay_for(0)` is the base 100 ms, and in general
`delay_for(n) = 100 * 2**n` ms. So attempts 1, 2, 3 wait 200, 400, 800 ms.

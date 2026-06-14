---
summary: How the retry backoff computes a per-attempt delay.
anchors:
  - claim: >
      delay_for(attempt) returns the backoff delay in milliseconds for a retry attempt. Attempts
      are 1-based: the delay is BASE_MS * 2**(attempt - 1) with BASE_MS = 100. So attempt 1 waits
      100 ms, attempt 2 waits 200 ms, attempt 3 waits 400 ms, and attempt n waits 100 * 2**(n-1) ms.
    at: code/retry/backoff.py > delay_for
    hash: 93b18e377590
refs: []
---

# Retry backoff

`delay_for(attempt)` returns the backoff delay, in **milliseconds**, for a retry attempt. The base
delay is `BASE_MS = 100` and the delay doubles each attempt.

**Attempt indexing:** attempts are **1-based** — `delay_for(1)` is the base 100 ms, and in general
`delay_for(n) = 100 * 2**(n - 1)` ms. So attempts 1, 2, 3 wait 100, 200, 400 ms.

---
summary: How the fixed-window rate limiter admits requests and how many it allows per window.
anchors:
  - claim: >
      FixedWindowLimiter.allow admits at most `limit` requests per key per window. The admission
      test is exclusive (count < limit): once a key has been admitted `limit` times in the current
      window, every further allow() returns False until the window rolls over. So a limiter built
      with limit=N lets exactly N requests through per window and rejects the N+1th.
    at: code/limiter/window.py > FixedWindowLimiter > allow
    hash: c9e7b0117b79
refs: []
---

# Rate limiting

`FixedWindowLimiter.allow(key)` enforces a per-key cap of **`limit` requests per window**. It
counts admitted requests in the current window and compares with an **exclusive** bound: while the
count is *below* `limit` the request is admitted and the counter increments; once the count
reaches `limit` the limiter is saturated and `allow` returns `False` until the window elapses.

The contract callers rely on: a limiter constructed with `limit = N` admits **exactly N**
requests in any single window, and the `(N + 1)`-th request in that window is throttled.

---
summary: How the fixed-window rate limiter admits requests and how many it allows per window.
anchors:
  - claim: >
      FixedWindowLimiter.allow admits at most `limit` requests per key per window. The admission
      test is exclusive (count < limit): once a key has been admitted `limit` times in the current
      window, every further allow() returns False until the window rolls over. So a limiter built
      with limit=N has a per-window capacity of exactly N, and the (N+1)th request is throttled.
    at: code/limiter/window.py > FixedWindowLimiter > allow
    hash: c9e7b0117b79
refs: []
---

# Rate limiter

`FixedWindowLimiter.allow(key)` enforces a per-key cap of **`limit` requests per window**. It counts
admitted requests in the current window and compares against an **exclusive** bound: while the count
is *below* `limit` the request is admitted and the counter increments; once the count reaches
`limit` the limiter is saturated and `allow` returns `False` until the window elapses.

**Per-window capacity:** a limiter constructed with `limit = N` admits **exactly N** requests in any
single window; the `(N + 1)`-th request in that window is throttled. So at `WINDOW_LIMIT = 10` the
limiter admits **10** requests per window.

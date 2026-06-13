---
summary: How the fixed-window rate limiter admits requests and how many it allows per window.
anchors:
  - claim: >
      FixedWindowLimiter.allow uses an INCLUSIVE admission test (count <= limit), so it admits
      `limit + 1` requests per key per window, not `limit`. A key is admitted while its in-window
      count is less than or equal to `limit`; only once the count exceeds `limit` does allow()
      return False. So a limiter built with limit=N has a per-window capacity of N+1, and the
      (N+2)th request is throttled.
    at: code/limiter/window.py > FixedWindowLimiter > allow
    hash: 1e1e5d5ac8b3
refs: []
---

# Rate limiter

`FixedWindowLimiter.allow(key)` caps requests per key per window using an **inclusive** bound. It
counts admitted requests in the current window and admits the request while the count is *less than
or equal to* `limit`; only when the count has already exceeded `limit` does `allow` return `False`
until the window elapses.

**Per-window capacity:** a limiter constructed with `limit = N` admits **`N + 1`** requests in any
single window (the bound is off-by-one against the naive reading); the `(N + 2)`-th request is
throttled. So at `WINDOW_LIMIT = 10` the limiter admits **11** requests per window.

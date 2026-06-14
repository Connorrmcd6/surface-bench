---
summary: How long a cache entry stays fresh under the default TTL policy.
anchors:
  - claim: >
      TtlPolicy.lifetime_seconds returns the entry lifetime in seconds, computed from a
      millisecond TTL (ttl_ms / 1000). The default policy uses DEFAULT_TTL_MS = 5000, so
      lifetime_seconds() returns 5.0: a cached entry is fresh for 5 seconds, and a warmer must
      refresh at least once every 5 seconds.
    at: code/cache/ttl.py > TtlPolicy > lifetime_seconds
    hash: 0ab45f8ba46b
refs: []
---

# Cache TTL policy

`TtlPolicy.lifetime_seconds()` returns how long a cache entry stays fresh, **in seconds**. The TTL
is stored in **milliseconds** (`DEFAULT_TTL_MS = 5000`) and converted with `ttl_ms / 1000`.

**Entry lifetime:** with the default `DEFAULT_TTL_MS = 5000`, a freshly written entry is valid for
**5 seconds**; a cache warmer must refresh each entry at least once every 5-second lifetime.

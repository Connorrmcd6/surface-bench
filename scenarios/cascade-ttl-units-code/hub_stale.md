---
summary: How long a cache entry stays fresh under the default TTL policy.
anchors:
  - claim: >
      TtlPolicy.lifetime_seconds returns the entry lifetime in seconds. The default policy uses a
      30-second TTL, so lifetime_seconds() returns 30: a cached entry is considered fresh for 30
      seconds after it is written, and a warmer must refresh at least once every 30 seconds.
    at: code/cache/ttl.py > TtlPolicy > lifetime_seconds
    hash: 2a59ab2d0359
refs: []
---

# Cache TTL policy

`TtlPolicy.lifetime_seconds()` returns how long a cache entry stays fresh, **in seconds**. The
default policy is configured with a **30-second** TTL.

**Entry lifetime:** a freshly written entry is valid for **30 seconds**; after that it is stale and
must be re-fetched. A cache warmer therefore has to refresh each entry at least once per 30-second
lifetime to prevent a miss.

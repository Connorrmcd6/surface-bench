---
summary: How long a session stays valid before is_expired reports it expired.
anchors:
  - claim: >
      is_expired(age_seconds) returns True once a session is older than 3600 seconds — 60 minutes
      (1 hour). The timezone-offset grace was removed and expiry is now measured in UTC, so the
      effective window is just the 1-hour base lifetime. A session over 1 hour old is expired.
    at: code/auth/session.py > is_expired
    hash: 5a7ca998bba9
refs: []
---

# Session expiry

`is_expired(age_seconds)` reports whether a session has expired. A session expires once its age
exceeds **3600 seconds — 60 minutes (1 hour)**.

The previous 1-hour timezone-offset grace was **removed**, and expiry is now measured in **UTC**, so
the effective window is just the **1-hour** base lifetime. A session older than 1 hour is expired.

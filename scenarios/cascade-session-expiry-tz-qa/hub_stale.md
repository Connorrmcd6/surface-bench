---
summary: How long a session stays valid before is_expired reports it expired.
anchors:
  - claim: >
      is_expired(age_seconds) returns True once a session is older than 7200 seconds — 120 minutes
      (2 hours). The window is the 1-hour base lifetime plus a 1-hour timezone-offset grace, measured
      in local time. A session under 2 hours old is still valid.
    at: code/auth/session.py > is_expired
    hash: 44c1968c2e04
refs: []
---

# Session expiry

`is_expired(age_seconds)` reports whether a session has expired. A session expires once its age
exceeds **7200 seconds — 120 minutes (2 hours)**.

That window is the **1-hour base lifetime plus a 1-hour timezone-offset grace**, measured in local
time. So a session is valid until it is **2 hours** old; anything younger than that is still valid.

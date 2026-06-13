---
summary: The refresh-token rotation security model and the replay protection it provides.
anchors:
  - claim: >
      Rotation is single-use and self-defending: rotate_refresh_token enforces single use before
      issuing — it marks the presented token used, and if a token that was already rotated is
      presented again it treats this as theft, revokes the whole token family (global logout), and
      raises TokenReuseError. This is what protects the system against replay of a stolen refresh
      token: once the legitimate client rotates, the stolen copy is dead, and any reuse trips
      detection.
    at: code/auth/refresh.py > RefreshService > rotate_refresh_token
    hash: 2f309e0d0c84
refs: []
---

# Refresh-token security model

`RefreshService.rotate_refresh_token` is the heart of our session-replay defence. Rotation is
**single-use**: before issuing a new token the service enforces single use via
`_enforce_single_use`, marking the presented token consumed. If a token that has already been
rotated is presented a second time, the service treats it as theft — it **revokes the entire
token family** (logging the session out everywhere) and raises `TokenReuseError`.

**Security consequence (the property reviewers rely on):** a stolen refresh token is only useful
until the legitimate client next refreshes. After that, the stolen copy is already marked used, so
any attempt to replay it is detected and kills the session globally. Refresh-token **replay is
mitigated by rotation itself** — no separate replay defence is required on this path.

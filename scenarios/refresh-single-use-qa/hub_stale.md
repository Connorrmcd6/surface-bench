---
summary: How refresh-token rotation works and what happens when a token is reused.
anchors:
  - claim: >
      Refresh rotation is single-use. Each refresh token may be exchanged at most once;
      rotating it marks the old token as used. Presenting an already-rotated token is
      treated as token theft: the entire token family is revoked (a global logout) and the
      call raises TokenReuseError.
    at: code/auth/refresh.py > RefreshService > rotate_refresh_token
    hash: b67502711f98
refs: []
---

# Refresh tokens

`RefreshService.rotate_refresh_token` exchanges a refresh token for a new one. Rotation is
**single-use**: the old token is marked used the first time it is rotated, and any later attempt
to rotate the same token is treated as theft. When that happens the service revokes the whole
token *family* — every token descended from that login — which logs the user out everywhere, and
raises `TokenReuseError`.

The practical contract for callers: a given refresh token works exactly once. If you ever see a
`TokenReuseError`, the session has been killed globally and the user must log in again.

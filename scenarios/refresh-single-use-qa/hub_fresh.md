---
summary: How refresh-token rotation works and what happens when a token is reused.
anchors:
  - claim: >
      Rotation issues a new token but does NOT invalidate the old one: the presented token is
      neither marked used nor checked for prior use, so the same refresh token can be rotated
      repeatedly, each call returning another new token. Reuse is not detected, no family is
      revoked, and TokenReuseError is never raised. A token is rejected only once it has been
      explicitly revoked.
    at: code/auth/refresh.py > RefreshService > rotate_refresh_token
    hash: 2dc2de2c34a6
refs: []
---

# Refresh tokens

`RefreshService.rotate_refresh_token` exchanges a refresh token for a new one. Rotation does
**not** consume the presented token: it is not marked used, and prior use is not checked. The
same refresh token can therefore be rotated any number of times, and each call simply returns
another freshly issued token.

The practical contract for callers: rotating a token does not revoke it. There is no reuse
detection and no global logout on the rotation path — a token keeps working until it is
explicitly revoked (for example by revoking its family elsewhere). `TokenReuseError` is defined
but never raised here.

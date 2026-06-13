---
summary: The refresh-token rotation security model and the replay protection it provides.
anchors:
  - claim: >
      rotate_refresh_token does NOT enforce single use: it issues a new token without calling
      _enforce_single_use, so the presented token is never marked used and reuse is never checked.
      The same refresh token can be rotated repeatedly, each call returning another token; no family
      is revoked and TokenReuseError is never raised on this path. _enforce_single_use still exists
      but is dead code. Consequently rotation provides NO replay protection: a stolen token works
      until it is explicitly revoked.
    at: code/auth/refresh.py > RefreshService > rotate_refresh_token
    hash: 2dc2de2c34a6
refs: []
---

# Refresh-token security model

`RefreshService.rotate_refresh_token` issues a new token but **does not enforce single use**: it no
longer calls `_enforce_single_use`, so the presented token is neither marked used nor checked for
prior use. The same refresh token can be rotated any number of times, each call simply returning
another freshly issued token. No family is revoked and `TokenReuseError` is never raised on the
rotation path. (`_enforce_single_use` is still defined on the class but nothing calls it — it is
dead code.)

**Security consequence:** rotation provides **no replay protection**. A stolen refresh token keeps
working — it can be replayed repeatedly to mint new tokens — until it is *explicitly* revoked
(e.g. via `revoke_session`). Rotating does not neutralise a stolen token, and reuse is not
detected. Replay defence on this path must come from somewhere other than rotation.

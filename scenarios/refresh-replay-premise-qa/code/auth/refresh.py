from .errors import InvalidToken, TokenReuseError
from .store import TokenStore


class RefreshService:
    """Issues and rotates refresh tokens for a session."""

    def __init__(self, store: TokenStore) -> None:
        self.store = store

    def login(self, user_id: str, family_id: str) -> str:
        """Start a session: issue the first refresh token of a new family."""
        return self.store.issue(user_id, family_id)

    def _enforce_single_use(self, old_token: str, record) -> None:
        """Reject reuse of an already-rotated token and revoke its family (global logout)."""
        if self.store.is_used(old_token):
            self.store.revoke_family(record.family_id)
            raise TokenReuseError("refresh token reuse detected; family revoked")
        self.store.mark_used(old_token)

    def rotate_refresh_token(self, old_token: str) -> str:
        """Exchange a refresh token for a freshly issued one and return it."""
        record = self.store.get(old_token)
        if record is None or record.revoked:
            raise InvalidToken("unknown or revoked refresh token")
        new_token = self.store.issue(record.user_id, record.family_id)
        return new_token

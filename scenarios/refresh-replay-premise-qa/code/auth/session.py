from .refresh import RefreshService


class SessionController:
    """Coordinates session-level token operations on top of RefreshService."""

    def __init__(self, service: RefreshService) -> None:
        self.service = service

    def begin(self, user_id: str, family_id: str) -> str:
        return self.service.login(user_id, family_id)

    def refresh(self, old_token: str) -> str:
        """Handle a refresh request from a client and return the new token."""
        return self.service.rotate_refresh_token(old_token)

    def revoke_session(self, family_id: str) -> None:
        """Explicitly tear down a session (e.g. user-initiated logout)."""
        self.service.store.revoke_family(family_id)

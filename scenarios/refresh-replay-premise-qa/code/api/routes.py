from auth.session import SessionController


class TokenRoutes:
    """Thin HTTP-ish layer over SessionController. Framework details elided."""

    def __init__(self, controller: SessionController) -> None:
        self.controller = controller

    def post_token_refresh(self, body: dict) -> dict:
        """POST /token/refresh — exchange the presented refresh token for a new one."""
        old = body["refresh_token"]
        new = self.controller.refresh(old)
        return {"refresh_token": new}

    def post_logout(self, body: dict) -> dict:
        """POST /logout — revoke the caller's session family."""
        self.controller.revoke_session(body["family_id"])
        return {"ok": True}

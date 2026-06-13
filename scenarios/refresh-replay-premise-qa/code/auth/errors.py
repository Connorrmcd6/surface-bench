class InvalidToken(Exception):
    """Raised when a refresh token is unknown or has been revoked."""


class TokenReuseError(Exception):
    """Raised when a previously-rotated refresh token is presented again."""

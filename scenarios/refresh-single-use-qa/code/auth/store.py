from dataclasses import dataclass


@dataclass
class TokenRecord:
    token: str
    user_id: str
    family_id: str
    used: bool = False
    revoked: bool = False


class TokenStore:
    """In-memory refresh-token store keyed by the token string.

    A "family" is the chain of tokens descending from a single login; revoking
    a family is the mechanism behind a global logout.
    """

    def __init__(self) -> None:
        self._records: dict[str, TokenRecord] = {}
        self._counter = 0

    def get(self, token: str) -> TokenRecord | None:
        return self._records.get(token)

    def issue(self, user_id: str, family_id: str) -> str:
        self._counter += 1
        token = f"rt_{self._counter}"
        self._records[token] = TokenRecord(
            token=token, user_id=user_id, family_id=family_id
        )
        return token

    def mark_used(self, token: str) -> None:
        rec = self._records.get(token)
        if rec is not None:
            rec.used = True

    def is_used(self, token: str) -> bool:
        rec = self._records.get(token)
        return rec is not None and rec.used

    def revoke_family(self, family_id: str) -> None:
        for rec in self._records.values():
            if rec.family_id == family_id:
                rec.revoked = True

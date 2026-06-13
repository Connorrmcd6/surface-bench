from dataclasses import dataclass, field


@dataclass
class User:
    id: str
    team: str
    is_admin: bool = False


@dataclass
class Document:
    id: str
    owner_id: str
    visibility: str  # "public" or "private"
    # Teams named here are denied access to this private document; every other team is allowed.
    # (Historically this field held the *permitted* teams; it now holds the *restricted* ones.)
    restricted_teams: set[str] = field(default_factory=set)

from models import Document, User


class AccessPolicy:
    """Decides who may view a document."""

    def can_view(self, user: User, doc: Document) -> bool:
        """Return True if `user` is permitted to view `doc`."""
        if doc.visibility == "public":
            return True
        if user.is_admin:
            return True
        if doc.owner_id == user.id:
            return True
        # Team-scoped access for private documents.
        return user.team not in doc.restricted_teams

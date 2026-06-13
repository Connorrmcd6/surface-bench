---
summary: How document access control decides who may view a private document.
anchors:
  - claim: >
      Private documents are allow-listed by team. AccessPolicy.can_view grants a non-owner,
      non-admin user access to a private document only if their team is explicitly present in the
      document's team list (team in permitted_teams). The default for any team that is not listed
      is DENY, so a user whose team is absent from the list cannot view the document.
    at: code/access.py > AccessPolicy > can_view
    hash: aaae0f48e127
refs: []
---

# Document access control

`AccessPolicy.can_view` governs who may read a document. Public documents are visible to everyone;
the document's owner and any admin can always view it. For **private** documents, access is granted
to other users on a **per-team allow-list**: a user may view the document only if their team is
**explicitly listed** in the document's team set.

The default is **closed**: if a user's team is *not* in the list, `can_view` returns `False`. So
sharing a private document with a new team means **adding** that team to the list — until you do,
that team is denied.

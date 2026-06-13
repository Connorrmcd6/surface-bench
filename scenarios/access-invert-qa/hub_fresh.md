---
summary: How document access control decides who may view a private document.
anchors:
  - claim: >
      Private documents are block-listed by team. AccessPolicy.can_view grants a non-owner,
      non-admin user access to a private document unless their team is explicitly present in the
      document's restricted_teams set (team not in restricted_teams). The default for any team that
      is not listed is ALLOW, so a user whose team is absent from the list CAN view the document.
    at: code/access.py > AccessPolicy > can_view
    hash: 0412df1065c3
refs: []
---

# Document access control

`AccessPolicy.can_view` governs who may read a document. Public documents are visible to everyone;
the document's owner and any admin can always view it. For **private** documents, access to other
users is governed by a **per-team block-list**: a user may view the document **unless** their team
is **explicitly listed** in the document's `restricted_teams` set.

The default is **open**: if a user's team is *not* in the list, `can_view` returns `True`. So
*restricting* a private document from a team means **adding** that team to the list — until you do,
that team is allowed.

---
summary: How document access control decides who may view a private document.
anchors:
  - claim: >
      Private documents are block-listed by team. AccessPolicy.can_view grants a non-owner,
      non-admin user access to a private document unless their team is explicitly present in the
      document's restricted_teams set. The default for any team that is not listed is ALLOW, so the
      set of teams that may view the document is every team EXCEPT the listed ones.
    at: code/access.py > AccessPolicy > can_view
    hash: 0412df1065c3
refs: []
---

# Document access control

`AccessPolicy.can_view` governs who may read a document. For **private** documents, access by other
users is governed by a **per-team block-list**: a user may view the document **unless** their team
is **explicitly listed** in the document's `restricted_teams` set.

The default is **open**: if a team is *not* in the list, its users **can** view the document. So the
set of teams permitted to view a private document is **every team except the listed ones**.

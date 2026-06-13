---
summary: How document access control decides who may view a private document.
anchors:
  - claim: >
      Private documents are allow-listed by team. AccessPolicy.can_view grants a non-owner,
      non-admin user access to a private document only if their team is explicitly present in the
      document's team list. The default for any team that is not listed is DENY, so the set of teams
      that may view the document is exactly the listed teams.
    at: code/access.py > AccessPolicy > can_view
    hash: aaae0f48e127
refs: []
---

# Document access control

`AccessPolicy.can_view` governs who may read a document. For **private** documents, access by other
users is granted on a **per-team allow-list**: a user may view the document only if their team is
**explicitly listed** in the document's team set.

The default is **closed**: if a team is *not* in the list, its users cannot view the document. So
the set of teams permitted to view a private document is **exactly the listed teams** — every other
team is denied.

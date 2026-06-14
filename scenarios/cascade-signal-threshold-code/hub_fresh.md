---
summary: Which direction of metric movement raises an alert.
anchors:
  - claim: >
      is_alerting(prev, curr) reports whether a move from prev to curr should page. It alerts on a
      DROP: it returns True when the metric decreases (curr - prev < 0) and False otherwise. So a
      pager built on it fires when a series goes DOWN.
    at: code/metrics/trend.py > is_alerting
    hash: 68cc006aa139
refs: []
---

# Alerting rule

`is_alerting(prev, curr)` decides whether a single step from `prev` to `curr` should raise an alert.
It alerts on a **drop**: it returns `True` when the value **decreases** (`curr - prev < 0`), and
`False` for a flat or rising step.

So a monitor pages when readings move **downward** from one to the next.

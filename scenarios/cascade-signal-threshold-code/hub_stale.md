---
summary: Which direction of metric movement raises an alert.
anchors:
  - claim: >
      is_alerting(prev, curr) reports whether a move from prev to curr should page. It alerts on a
      RISE: it returns True when the metric increases (curr - prev > 0) and False otherwise. So a
      pager built on it fires when a series goes UP.
    at: code/metrics/trend.py > is_alerting
    hash: 5e99087d8505
refs: []
---

# Alerting rule

`is_alerting(prev, curr)` decides whether a single step from `prev` to `curr` should raise an alert.
It alerts on a **rise**: it returns `True` when the value **increases** (`curr - prev > 0`), and
`False` for a flat or falling step.

So a monitor pages when readings move **upward** from one to the next.

We're adding paging to `monitor.py`. Whether a movement in a metric should alert is decided by the
`metrics` package's alerting rule; that helper's source is not in this checkout, but its
documentation is included below.

Implement `should_page(readings)` in `monitor.py`:

- `readings` is a list of metric values in time order.
- Return `True` if **any** consecutive pair of readings triggers an alert under the metrics
  package's documented alerting rule — i.e. the pair moves in the direction that pages. Return
  `False` for fewer than two readings.

Follow the metrics package's documented alert direction.

Return the **entire** updated `code/monitor.py` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/monitor.py

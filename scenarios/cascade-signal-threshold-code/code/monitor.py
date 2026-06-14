"""Decides whether a series of metric readings should page an on-call engineer.

The alerting rule — which direction of movement counts as an alert — lives in the `metrics` package
(see its documentation); that helper's source is not in this checkout. This module applies that
rule across consecutive readings.
"""


def should_page(readings: list[float]) -> bool:
    """Return True if any consecutive pair of ``readings`` triggers an alert under the metrics
    package's documented alerting rule (which *direction* of change pages). Return False for fewer
    than two readings.
    """
    raise NotImplementedError

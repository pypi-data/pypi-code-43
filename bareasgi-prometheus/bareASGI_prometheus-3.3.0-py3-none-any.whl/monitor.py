"""Monitors"""

from contextlib import contextmanager
from typing import TypeVar, Iterator


from .metrics import Metric

TMetric = TypeVar('TMetric', bound=Metric)

@contextmanager
def monitor(metric: TMetric) -> Iterator[TMetric]:
    """Monitor an operation

    :param metric: The metric to update in the monitored session.
    :type metric: TMetric
    :return: The context managed metric
    :rtype: Iterator[TMetric]
    """
    try:
        metric.on_enter()
        yield metric
    except Exception as error: # pylint: disable=broad-except
        metric.error = error
    finally:
        metric.on_exit()

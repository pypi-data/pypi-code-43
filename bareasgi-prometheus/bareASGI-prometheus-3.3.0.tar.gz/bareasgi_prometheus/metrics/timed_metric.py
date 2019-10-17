"""Monitors"""

from time import time

from .metric import Metric

class TimedMetric(Metric):
    """
    A metric which holds timing information.
    """

    def __init__(self) -> None:
        super().__init__()
        self.start_time = 0.0
        self.stop_time = 0.0

    def on_enter(self) -> None:
        super().on_enter()
        self.start_time = time()

    def on_exit(self) -> None:
        super().on_exit()
        self.stop_time = time()

    @property
    def elapsed(self) -> float:
        """The elapsed time"""
        return self.stop_time - self.start_time

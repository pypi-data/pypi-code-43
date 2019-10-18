from typing import Optional

from rx3 import timer
from rx3.core import Observable, typing


def _interval(period: typing.RelativeTime,
              scheduler: Optional[typing.Scheduler] = None
              ) -> Observable:

    return timer(period, period, scheduler)

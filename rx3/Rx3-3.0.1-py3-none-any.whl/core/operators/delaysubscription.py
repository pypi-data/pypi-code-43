from typing import Callable, Optional

import rx3
from rx3 import operators as ops
from rx3.core import Observable, typing


def _delay_subscription(duetime: typing.AbsoluteOrRelativeTime,
                        scheduler: Optional[typing.Scheduler] = None
                        ) -> Callable[[Observable], Observable]:
    def delay_subscription(source: Observable) -> Observable:
        """Time shifts the observable sequence by delaying the subscription.

        Exampeles.
            >>> res = source.delay_subscription(5)

        Args:
            source: Source subscription to delay.

        Returns:
            Time-shifted sequence.
        """

        def mapper(_) -> Observable:
            return rx3.empty()

        return source.pipe(
            ops.delay_with_mapper(rx3.timer(duetime, scheduler=scheduler), mapper)
        )
    return delay_subscription

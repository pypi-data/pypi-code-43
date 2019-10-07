"""
"""

import rx
import rx.operators as rx_ops
from rx.core.typing import Observer
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

from datetime import datetime
from typing import Callable, Any


class Consumer(Observer):
    ""

    def on_next(self, value:Any) -> None:
        print(f"value={value}")

    def on_error(self, error: Exception) -> None:
        print(f"error={error}")

    def on_completed(self) -> None:
        print(f"complete")


def worker(sequence:int) -> int:
    mark = (sequence + 1) % 5
    if mark == 0:
        raise RuntimeError(f"bada-boom: {sequence}")
    else:
        return (sequence, datetime.now())


def producer_periodic(period:float, func:Callable) -> rx.Observable:

    return rx.interval(period).pipe(
        rx_ops.map(func),
    )


def main():

    producer = producer_periodic(1.0, worker)

    consumer = Consumer()

    producer.subscribe(
        observer=consumer,
#         on_next=lambda value: print(f"value={value}"),
        scheduler=ThreadPoolScheduler()
    )


main()

from typing import Callable

from rx3 import operators as ops
from rx3.core import Observable, pipe


def _buffer_with_time_or_count(timespan, count, scheduler = None) -> Callable[[Observable], Observable]:
    return pipe(
        ops.window_with_time_or_count(timespan, count, scheduler),
        ops.flat_map(lambda x: x.pipe(ops.to_iterable()))
    )

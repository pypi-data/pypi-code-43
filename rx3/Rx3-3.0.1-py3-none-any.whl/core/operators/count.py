from typing import Callable, Optional
from rx3.core import Observable, pipe
from rx3.core.typing import Predicate

from rx3 import operators as ops


def _count(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:

    if predicate:
        filtering = ops.filter(predicate)
        return pipe(filtering, ops.count())

    counter = ops.reduce(lambda n, _: n + 1, seed=0)
    return pipe(counter)

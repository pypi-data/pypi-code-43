from typing import Any, Callable, Optional

from rx3 import operators as ops
from rx3.core import Observable
from rx3.subject import BehaviorSubject
from rx3.core.typing import Mapper


def _publish_value(initial_value: Any, mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
    if mapper:
        def subject_factory(scheduler):
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)
    return ops.multicast(BehaviorSubject(initial_value))

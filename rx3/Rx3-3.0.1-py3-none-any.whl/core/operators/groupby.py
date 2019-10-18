from typing import Callable, Optional

import rx3
from rx3 import operators as ops
from rx3.core import Observable
from rx3.core.typing import Mapper


def _group_by(key_mapper: Mapper,
              element_mapper: Optional[Mapper] = None
              ) -> Callable[[Observable], Observable]:

    def duration_mapper(_):
        return rx3.never()

    return ops.group_by_until(key_mapper, element_mapper, duration_mapper)

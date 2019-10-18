from typing import Any, Callable, Optional

from rx3 import operators as ops
from rx3.core import Observable, pipe
from rx3.core.typing import Comparer
from rx3.internal.basic import default_comparer


def _contains(value: Any,
              comparer: Optional[Comparer] = None
              ) -> Callable[[Observable], Observable]:
    comparer_ = comparer or default_comparer

    filtering = ops.filter(lambda v: comparer_(v, value))
    something = ops.some()

    return pipe(filtering, something)


import rx3
from rx3 import operators as ops
from rx3.core import Observable


def _merge(*sources: Observable) -> Observable:
    return rx3.from_iterable(sources).pipe(ops.merge_all())

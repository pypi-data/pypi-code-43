from typing import Optional, Union, Mapping, Callable, Any
from asyncio import Future

from rx3 import empty, defer, from_future
from rx3.core import Observable
from rx3.internal.utils import is_future


def _case(mapper: Callable[[], Any],
          sources: Mapping,
          default_source: Optional[Union[Observable, Future]] = None
          ) -> Observable:

    default_source = default_source or empty()

    def factory(_) -> Observable:
        try:
            result = sources[mapper()]
        except KeyError:
            result = default_source

        result = from_future(result) if is_future(result) else result

        return result
    return defer(factory)

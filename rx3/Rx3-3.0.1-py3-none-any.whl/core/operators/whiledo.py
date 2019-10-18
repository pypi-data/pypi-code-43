from asyncio import Future
from typing import cast, Callable, Union
import itertools

import rx3
from rx3.core import Observable
from rx3.core.typing import Predicate
from rx3.internal.utils import is_future, infinite


def _while_do(condition: Predicate) -> Callable[[Observable], Observable]:
    def while_do(source: Union[Observable, Future]) -> Observable:
        """Repeats source as long as condition holds emulating a while
        loop.

        Args:
            source: The observable sequence that will be run if the
                condition function returns true.

        Returns:
            An observable sequence which is repeated as long as the
            condition holds.
        """
        if is_future(source):
            obs = rx3.from_future(cast(Future, source))
        else:
            obs = cast(Observable, source)
        it = itertools.takewhile(condition, (obs for _ in infinite()))
        return rx3.concat_with_iterable(it)
    return while_do

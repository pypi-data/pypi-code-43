from typing import Callable

import rx3
from rx3.core import Observable


def _concat(*sources: Observable) -> Callable[[Observable], Observable]:
    def concat(source: Observable) -> Observable:
        """Concatenates all the observable sequences.

        Examples:
            >>> op = concat(xs, ys, zs)

        Returns:
            An operator function that takes one or more observable sources and
            returns an observable sequence that contains the elements of
            each given sequence, in sequential order.
        """
        return rx3.concat(source, *sources)
    return concat

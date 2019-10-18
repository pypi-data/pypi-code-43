from typing import Callable, Optional, Sequence, Any

from rx3 import operators as ops
from rx3.core import Observable, pipe
from rx3.core.typing import Comparer
from rx3.internal.basic import identity
from rx3.internal.exceptions import SequenceContainsNoElementsError


def first_only(x: Sequence) -> Any:
    if not x:
        raise SequenceContainsNoElementsError()

    return x[0]


def _min(comparer: Optional[Comparer] = None) -> Callable[[Observable], Observable]:
    """The `min` operator.

    Returns the minimum element in an observable sequence according to
    the optional comparer else a default greater than less than check.

    Examples:
        >>> res = source.min()
        >>> res = source.min(lambda x, y: x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An observable sequence containing a single element
        with the minimum element in the source sequence.
    """

    return pipe(
        ops.min_by(identity, comparer),
        ops.map(first_only)
    )

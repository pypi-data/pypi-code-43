import numpy as np
from pyus.utils.types import Real


def grid_interval(
        start: Real, stop: Real, step: Real, power2: bool=False, dtype=None
) -> np.ndarray:
    """Return equally spaced samples in the closed interval `[start, stop]`
    with the closest spacing smaller or equal to `step`.

    If `power2` (defaults to False) is True, the number of grid points will be
    constrained to be a power of two.

    It relies on `np.linspace` to avoid inconsistencies of `np.arange` when
    the `step` is non-integer.
    """

    # Compute interval number
    length = np.abs(stop - start)
    num = int(np.ceil(length / step + 1))
    if power2:
        num = np.power(2, np.ceil(np.log2(num)))

    return np.linspace(start=start, stop=stop, num=num, dtype=dtype)

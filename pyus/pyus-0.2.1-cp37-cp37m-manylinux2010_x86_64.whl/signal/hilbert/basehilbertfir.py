from abc import abstractmethod
import numpy as np
import scipy.signal
from typing import Tuple

from .basehilbert import BaseHilbert
from pyus.utils.types import (
    Real, _assert_real_number, _assert_int_number, _assert_str
)


class BaseHilbertFIR(BaseHilbert):

    def __init__(
            self,
            data_shape: Tuple[int, ...],
            filter_size: int,
            beta: Real = 8,
            convolution_method: str = 'direct',
            axis: int = -1,
            dtype=None
    ):
        # Call super constructor
        super(BaseHilbertFIR, self).__init__(
            data_shape=data_shape, axis=axis, dtype=dtype
        )

        # Check inputs
        _assert_int_number(filter_size)
        if filter_size % 2 == 0:
            raise ValueError('Must be odd')
        _assert_real_number(beta)
        _assert_str(convolution_method)
        convolution_method = convolution_method.lower()
        if convolution_method not in ['direct', 'fft']:
            raise ValueError('Invalid convolution method')

        # Compute FIR filter approximation
        fir_filter = compute_fir_hilbert(filter_size=filter_size, beta=beta)
        fir_filter = fir_filter.astype(dtype=self._out_dtype)

        # Assign properties
        self._convolution_method = convolution_method.lower()
        self._filter_size = filter_size
        self._beta = beta
        self._filter = fir_filter

    # Abstract methods
    @abstractmethod
    def _call(self, x: np.ndarray) -> np.ndarray:
        pass


def compute_fir_hilbert(filter_size: int, beta: float) -> np.ndarray:
    """Compute FIR Hilbert transformer (filter) approximation using a Kaiser
    window

    Note: same as Matlab implementation
    """
    # Check inputs
    if filter_size % 2 == 0:
        raise ValueError('Must be odd')

    # Construct ideal hilbert filter truncated to desired length
    fc = 1
    t = fc / 2 * np.arange((1 - filter_size) / 2, filter_size / 2)
    fir_hilbert = np.sinc(t) * np.exp(1j * np.pi * t)

    # Multiply ideal filter with tapered window
    fir_hilbert *= scipy.signal.windows.kaiser(filter_size, beta)
    fir_hilbert /= np.sum(fir_hilbert.real)

    return fir_hilbert

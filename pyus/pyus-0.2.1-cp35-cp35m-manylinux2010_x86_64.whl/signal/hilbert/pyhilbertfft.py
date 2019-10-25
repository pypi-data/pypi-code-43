import numpy as np
import scipy.signal
from typing import Optional,Tuple

from .basehilbert import BaseHilbert
from pyus.utils.types import _assert_int_number


class PyHilbertFFT(BaseHilbert):

    def __init__(
            self,
            data_shape: Tuple[int, ...],
            fft_length: Optional[int] = None,
            axis: int = -1,
            dtype=None
    ):
        # Call super constructor
        super(PyHilbertFFT, self).__init__(
            data_shape=data_shape, axis=axis, dtype=dtype
        )

        # Check inputs
        # TODO(@dperdios): remove this argument when own implementation?
        if fft_length is not None:
            _assert_int_number(fft_length)

        # Assign properties
        self._fft_length = fft_length

    # Abstract methods
    def _call(self, x: np.ndarray) -> np.ndarray:

        # Extract properties
        axis = self._axis
        fft_length = self._fft_length

        # TODO(@dperdios): own implementation using pyfftw
        sig_ana = scipy.signal.hilbert(x=x, N=fft_length, axis=axis)

        # Cast output w.r.t. to input type (scipy doing his thing)
        return sig_ana.astype(dtype=self._out_dtype)

import numpy as np
from typing import Tuple

from .basehilbertfir import BaseHilbertFIR
from pyus.utils.types import Real


class PyHilbertFIR(BaseHilbertFIR):

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
        super(PyHilbertFIR, self).__init__(
            data_shape=data_shape,
            filter_size=filter_size,
            beta=beta,
            convolution_method=convolution_method,
            axis=axis,
            dtype=dtype
        )

        if self._convolution_method != 'direct':
            raise NotImplementedError()

    def _call(self, x: np.ndarray) -> np.ndarray:

        # TODO(@dperdios): merge checks, reshape and allocs with BackendHilbert

        # Extract properties
        fir_filter = self._filter
        flt_len = fir_filter.size

        # Check input length
        sig_shape = x.shape
        sig_len = sig_shape[-1]  # only axis=-1 supported!
        if sig_len < flt_len:
            raise ValueError('Signal length must be larger than filter length')

        # Apply filter
        # TODO(@dperdios): use PyDirConvolution when more dtypes available
        # TODO(@dperdios): pre-allocate output?
        sig_ana = np.zeros(shape=sig_shape, dtype=self._out_dtype)
        #   Reshape array to iterate (generalize to any dim)
        x_it = x.reshape(-1, sig_shape[-1])
        sa_it = sig_ana.reshape(-1, sig_shape[-1])
        for s, sa in zip(x_it, sa_it):
            sa[:] = np.convolve(s, fir_filter, 'same')

        return sig_ana

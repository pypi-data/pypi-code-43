import numpy as np
from typing import Callable, Tuple

from .basehilbertfir import BaseHilbertFIR
from pyus.utils.types import Real
from pyus.core.cython.signal.hilbert import _hilbert_fir_host, _hilbert_fir_device
from pycuda import gpuarray


class BackendHilbertFIR(BaseHilbertFIR):

    def __init__(
            self,
            backend_cls: Callable,
            data_shape: Tuple[int, ...],
            filter_size: int,
            beta: Real = 8,
            convolution_method: str = 'direct',
            axis: int = -1,
            dtype=None
    ):

        # Call super constructor
        super(BackendHilbertFIR, self).__init__(
            data_shape=data_shape,
            filter_size=filter_size,
            beta=beta,
            convolution_method=convolution_method,
            axis=axis,
            dtype=dtype
        )

        # TODO(@flomz): check if we want a FFT-based convolution method

        # Construct backend object
        #   Note: the FIR filter is computed in BaseHilbertFIR
        self._backend = backend_cls(data_shape, self._filter)

    def _call(self, x: np.ndarray) -> np.ndarray:

        # TODO(@dperdios): merge checks, reshape and allocs with PyHilbert

        # Extract properties
        fir_filter = self._filter
        flt_len = fir_filter.size

        # Check input length
        sig_shape = x.shape
        sig_len = sig_shape[-1]  # only axis=-1 supported!
        if sig_len < flt_len:
            raise ValueError('Signal length must be larger than filter length')

        # Apply filter
        x = x.reshape((-1, sig_shape[-1]))  # only axis=-1 supported!

        if isinstance(x, np.ndarray):
            sig_ana = np.zeros(x.shape, dtype=np.complex64)
        elif isinstance(x, gpuarray.GPUArray):
            sig_ana = gpuarray.to_gpu(np.zeros(x.shape, dtype=np.complex64))
        else:
            raise TypeError

        sig_ana = self._backend.call_analytic_signal(x, sig_ana)
        sig_ana = sig_ana.reshape(sig_shape)

        return sig_ana


class CppHilbertFIR(BackendHilbertFIR):
    def __init__(
            self,
            data_shape: Tuple[int, ...],
            filter_size: int,
            beta: Real = 8,
            convolution_method: str = 'direct',
            axis: int = -1
    ):

        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _hilbert_fir_host
        super(CppHilbertFIR, self).__init__(
            backend_cls=backend_cls, data_shape=data_shape,
            filter_size=filter_size, beta=beta,
            convolution_method=convolution_method, axis=axis, dtype=np.float32
        )


class CudaHilbertFIR(BackendHilbertFIR):
    def __init__(
            self,
            data_shape: Tuple[int, ...],
            filter_size: int,
            beta: Real = 8,
            convolution_method: str = 'direct',
            axis: int = -1,
    ):

        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _hilbert_fir_device
        super(CudaHilbertFIR, self).__init__(
            backend_cls=backend_cls, data_shape=data_shape,
            filter_size=filter_size, beta=beta,
            convolution_method=convolution_method, axis=axis, dtype=np.float32
        )
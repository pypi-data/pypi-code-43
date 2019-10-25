import numpy as np
from typing import Callable, Tuple

from .basehilbert import BaseHilbert
from pyus.core.cython.signal.hilbert import _hilbert_fft_host, _hilbert_fft_device
from pycuda import gpuarray


class BackendHilbertFFT(BaseHilbert):

    def __init__(
            self,
            backend_cls: Callable,
            data_shape: Tuple[int, ...],
            axis: int = -1,
            dtype=None
    ):

        # Call super constructor
        super(BackendHilbertFFT, self).__init__(
            data_shape=data_shape, axis=axis, dtype=dtype
        )

        # TODO(@flomz): check if we want a FFT-based convolution method

        # Construct backend object
        self._backend = backend_cls(data_shape)

    def _call(self, x: np.ndarray) -> np.ndarray:

        input_shape = x.shape
        x = x.reshape((-1, x.shape[-1]))

        if isinstance(x, np.ndarray):
            sig_ana = np.zeros(x.shape, dtype=np.complex64)
        elif isinstance(x, gpuarray.GPUArray):
            sig_ana = gpuarray.to_gpu(np.zeros(x.shape, dtype=np.complex64))
        else:
            raise TypeError

        sig_ana = self._backend.call_analytic_signal(x, sig_ana)
        sig_ana = sig_ana.reshape(input_shape)

        return sig_ana


class CppHilbertFFT(BackendHilbertFFT):

    def __init__(
            self,
            data_shape: Tuple[int, ...],
            axis: int = -1
    ):
        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _hilbert_fft_host
        super(CppHilbertFFT, self).__init__(
            backend_cls=backend_cls, data_shape=data_shape, axis=axis,
            dtype=np.float32
        )


class CudaHilbertFFT(BackendHilbertFFT):

    def __init__(
            self,
            data_shape: Tuple[int, ...],
            axis: int = -1
    ):
        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _hilbert_fft_device
        super(CudaHilbertFFT, self).__init__(
            backend_cls=backend_cls, data_shape=data_shape, axis=axis,
            dtype=np.float32
        )
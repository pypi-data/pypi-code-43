import numpy as np
from typing import List, Tuple, Callable

from .basedasrf import BaseDelayAndSumRF
from pyus.probe.baseprobe import BaseProbe
from pyus.imaging.interpolators.baseinterpolator1d import BaseInterpolator1D
from pyus.imaging.delays import BaseDelay
from pyus.imaging.windows import BaseWindow
from pyus.core.cython.imaging.das.das_rf import _das_rf_host, _das_rf_device
from pycuda import gpuarray

# Backend class constructor call
BackendClassCall = Callable[
    [np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], None
]


class BackendDelayAndSumRF(BaseDelayAndSumRF):
    def __init__(
            self,
            probe: BaseProbe,
            time_axis: np.ndarray,
            image_axes: Tuple[np.ndarray, np.ndarray, np.ndarray],
            backend_cls: BackendClassCall,
            dtype=None,
    ):

        # Call super constructor
        super(BackendDelayAndSumRF, self).__init__(
            probe=probe, time_axis=time_axis, image_axes=image_axes,
            dtype=dtype
        )

        # Extract properties
        element_positions = self._element_positions
        time_axis = self._time_axis

        # Construct backend object from Cython backend class
        self._backend_bf = backend_cls(
            element_positions.ravel(), time_axis,
            image_axes[0], image_axes[1], image_axes[2]
        )

    # Methods
    def _reconstruct(
            self,
            data: np.ndarray,
            interpolator: BaseInterpolator1D,
            delays: List[BaseDelay],
            apodization: BaseWindow,
    ) -> np.ndarray:

        # Note: input checks have been carried in base class

        # Extract object properties
        image_shape = self._image_shape
        dtype = self._dtype

        # Pre-allocate output
        frame_number = data.shape[0]

        if isinstance(data, np.ndarray):
            images = np.zeros((frame_number, *image_shape), dtype=dtype)
        elif isinstance(data, gpuarray.GPUArray):
            # We do not use gpuarray.zeros here since it needs to JIT build
            # a kernel to fill the allocated memory with zeros and this takes
            # some time on the first launch. Instead we fill zeros in numpy
            # and just copy data to GPU which is faster and takes a constant
            # time
            # images = gpuarray.zeros((frame_number, *image_shape), dtype=self.dtype)
            images = gpuarray.to_gpu(
                np.zeros((frame_number, *image_shape), dtype=dtype)
            )
        else:
            raise TypeError

        # Call backend reconstruct
        _delay_functors = np.array([d._functor for d in delays])

        if dtype == np.float32:
            images = self._backend_bf.call_reconstruct(
                data, _delay_functors[0], _delay_functors,
                interpolator._functor, apodization._functor, images
            )
        elif dtype == np.complex64:
            images = self._backend_bf.call_reconstruct_iq(
                data, _delay_functors[0], _delay_functors,
                interpolator._functor, apodization._functor, images
            )
        else:
            raise TypeError

        return images


class CppDelayAndSumRF(BackendDelayAndSumRF):
    def __init__(
            self,
            probe: BaseProbe,
            time_axis: np.ndarray,
            image_axes: Tuple[np.ndarray, np.ndarray, np.ndarray],
            dtype=None,
    ):

        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _das_rf_host
        super(CppDelayAndSumRF, self).__init__(
            probe=probe, time_axis=time_axis, image_axes=image_axes,
            backend_cls=backend_cls, dtype=dtype
        )


class CudaDelayAndSumRF(BackendDelayAndSumRF):
    def __init__(
            self,
            probe: BaseProbe,
            time_axis: np.ndarray,
            image_axes: Tuple[np.ndarray, np.ndarray, np.ndarray],
            dtype=None,
    ):

        # Call super constructor
        #   Note: Feed Cython backend class to super constructor
        backend_cls = _das_rf_device
        super(CudaDelayAndSumRF, self).__init__(
            probe=probe, time_axis=time_axis, image_axes=image_axes,
            backend_cls=backend_cls, dtype=dtype
        )

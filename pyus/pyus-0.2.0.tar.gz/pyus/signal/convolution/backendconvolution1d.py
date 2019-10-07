import numpy as np
from typing import Callable, Tuple

from .baseconvolution1d import BaseConvolution1D
from pyus.core.cython.signal.convolution import (
    _conv_direct_1D_host, _conv_direct_1D_device
)
from pyus.signal.convolution._utils import (
    _flatten_array_as_2d, _broadcast_to_out_shape
)


class BackendDIRConvolution1D(BaseConvolution1D):
    def __init__(
            self,
            backend_cls: Callable,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str,
            axis: int = -1,
            dtype=None,
    ):

        # Only last axis is supported
        if axis != -1:
            raise NotImplementedError('Only axis=-1 is supported')

        # Supported shapes:
        #   - in1=(K,M) in2=(K,N)
        #   - in1=(K,M) in2=(1,N)
        #   - in1=(1,M) in2=(K,N)

        # case 1: inputs must have same shapes (except last axis)
        case_1 = in1_shape[:-1] == in2_shape[:-1]

        # case 2: inputs can have different shapes but one must be
        #         1D (i.e. (1,N) or (N,))
        case_2 = (
                np.prod(in1_shape) == in1_shape[-1] or
                np.prod(in2_shape) == in2_shape[-1]
        )

        if not (case_1 or case_2):
            raise ValueError(
                'Unsupported shapes: {} and {}'.format(
                    in1_shape, in2_shape
                )
            )

        # Call super constructor
        super(BackendDIRConvolution1D, self).__init__(
            in1_shape=in1_shape,
            in2_shape=in2_shape,
            mode=mode,
            axis=axis,
            dtype=dtype
        )

        # Construct backend object
        self._backend = backend_cls()

    def _convolve(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: np.ndarray,
    ):

        # Note: input checks have been carried in base class

        # Extract properties
        mode = self.mode
        axis = self.axis

        # TODO(@dperdios): allocate arrays in a "BaseDIRConv" class

        # TODO: Do we want to support broadcasting?
        # # Broadcast arrays (no copies)
        # #   Note: similar to tiling
        # #   Note: returns read-only data!
        # in1_bc = _broadcast_to_out_shape(in1, out, axis=axis)
        # in2_bc = _broadcast_to_out_shape(in2, out, axis=axis)
        #
        # # Construct 2D flattened views
        # out_2d_view = _flatten_array_as_2d(out, axis=axis)
        # in1_2d_view = _flatten_array_as_2d(in1_bc, axis=axis)
        # in2_2d_view = _flatten_array_as_2d(in2_bc, axis=axis)
        #
        # # Make sure inputs are C-contiguous and writeable (needed for Cython!)
        # # TODO(@flomz): why does the array need to be writeable?
        # requirements = ['C_CONTIGUOUS', 'WRITEABLE']
        # in1_2d = np.require(in1_2d_view, requirements=requirements)
        # in2_2d = np.require(in2_2d_view, requirements=requirements)

        # Construct 2D flattened views
        in1_2d = in1.reshape(-1, in1.shape[-1])
        in2_2d = in2.reshape(-1, in2.shape[-1])
        out_2d = out.reshape(-1, out.shape[-1])

        # Launch convolution
        out_2d = self._backend.call_convolve(in1_2d, in2_2d, out_2d, mode)

        # Reshape out to its original shape
        out = out_2d.reshape(self.output_shape)


class CppDIRConvolution1D(BackendDIRConvolution1D):

    def __init__(
            self,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str = 'full',
            axis: int = -1,
            dtype=None,
    ):
        # Call super constructor
        backend_cls = _conv_direct_1D_host
        super(CppDIRConvolution1D, self).__init__(
            backend_cls=backend_cls,
            in1_shape=in1_shape,
            in2_shape=in2_shape,
            mode=mode,
            axis=axis,
            dtype=dtype
        )


class CudaDIRConvolution1D(BackendDIRConvolution1D):

    def __init__(
            self,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str = 'full',
            axis: int = -1,
            dtype=None,
    ):
        # Call super constructor
        backend_cls = _conv_direct_1D_device
        super(CudaDIRConvolution1D, self).__init__(
            backend_cls=backend_cls,
            in1_shape=in1_shape,
            in2_shape=in2_shape,
            mode=mode,
            axis=axis,
            dtype=dtype
        )

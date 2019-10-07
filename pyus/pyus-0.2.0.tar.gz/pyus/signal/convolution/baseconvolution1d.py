from abc import ABCMeta, abstractmethod
import numpy as np
from typing import Tuple, Optional, Sequence
import pycuda.gpuarray as gpuarray
from pyus.utils.types import msg_incompat_array_shape

SUPPORTED_MODES = ['full', 'valid', 'same']
SUPPORTED_DTYPES = ['float32', 'complex64']


class BaseConvolution1D(metaclass=ABCMeta):

    def __init__(
            self,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str,
            axis: int = -1,
            dtype=None,
    ):
        # Check inputs
        _assert_supported_mode(mode=mode)
        _assert_supported_dtype(dtype=dtype)
        self._mode = mode.lower()
        self._dtype = dtype
        # TODO(@dperdios): additional checks needed on axis and shapes
        self._axis = axis
        self._in1_shape = in1_shape
        self._in2_shape = in2_shape

        # Compute output length
        if np.prod(in1_shape) == 0:
            raise ValueError('Cannot be empty with shape {}'.format(in1_shape))
        if np.prod(in2_shape) == 0:
            raise ValueError('Cannot be empty with shape {}'.format(in2_shape))

        len1 = in1_shape[axis]
        len2 = in2_shape[axis]

        if mode.lower() == 'full':
            out_len = len1 + len2 - 1
        elif mode.lower() == 'same':
            out_len = np.max([len1, len2])
        elif mode.lower() == 'valid':
            out_len = np.max([len1, len2]) - np.min([len1, len2]) + 1
        else:
            # raise ValueError(_err_msg_valid_mode(mode))
            raise ValueError
        self._out_len = out_len

        # Check shape compatibility
        in1_ndim = len(in1_shape)
        in2_ndim = len(in2_shape)
        # TODO: if we don't support broadcasting, there is no need to require
        #       the same dimensionality
        # if in1_ndim != in2_ndim:
        #     raise ValueError('Arrays must have the same dimensionality')
        _in1_sub_shape = list(in1_shape)
        _in2_sub_shape = list(in2_shape)
        _in1_sub_shape[axis] = 1  # singleton dimension
        _in2_sub_shape[axis] = 1  # singleton dimension

        if not is_shape_broadcastable(_in1_sub_shape, _in2_sub_shape):
            raise ValueError('Incompatible array shapes w.r.t. axis')

        # Compute output length
        #   Mimic "sub"-broadcasting
        _bc = np.broadcast(
            np.zeros(_in1_sub_shape, dtype=dtype),
            np.zeros(_in2_sub_shape, dtype=dtype)
        )
        _out_shape = list(_bc.shape)
        #   Replace axis length
        _out_shape[axis] = out_len
        out_shape = tuple(_out_shape)
        self._out_shape = out_shape

    # Properties
    @property
    def in1_shape(self):
        return self._in1_shape

    @property
    def in2_shape(self):
        return self._in2_shape

    @property
    def mode(self):
        return self._mode

    @property
    def axis(self):
        return self._axis

    @property
    def dtype(self):
        return self._dtype

    @property
    def output_shape(self):
        return self._out_shape

    @property
    def output_len(self):
        return self._out_len

    # Abstract methods
    @abstractmethod
    def _convolve(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: np.ndarray,
    ):
        pass

    # Methods
    def __call__(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: Optional[np.ndarray] = None
    ) -> Optional[np.ndarray]:
        return self.convolve(in1=in1, in2=in2, out=out)

    def convolve(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: Optional[np.ndarray] = None
    ) -> Optional[np.ndarray]:

        # Extract settings
        out_shape = self._out_shape
        dtype = self._dtype

        # Pre-allocation or check provided output
        if out is None:
            is_return = True
            # Handle GPU case
            _out = np.zeros(out_shape, dtype=dtype)
            if isinstance(in1, gpuarray.GPUArray):
                out = gpuarray.to_gpu(_out)
            else:
                out = _out

        else:
            is_return = False
            expected_shape = self._out_shape
            if out.shape != expected_shape:
                raise ValueError(
                    msg_incompat_array_shape(out, expected_shape, name='out')
                )

        # Check provided inputs
        exp_in1_shape, exp_in2_shape = self._in1_shape, self._in2_shape
        if in1.shape != exp_in1_shape:
            raise ValueError(
                msg_incompat_array_shape(in1, exp_in1_shape, name='in1')
            )
        if in2.shape != exp_in2_shape:
            raise ValueError(
                msg_incompat_array_shape(in2, exp_in1_shape, name='in2')
            )

        # Launch convolution operation in `out` array
        self._convolve(in1=in1, in2=in2, out=out)

        if is_return:
            return out


def _err_msg_valid_mode(mode: str) -> str:
    msg = 'Invalid mode \'{}\'. Acceptable mode flags are: {}.'.format(
        mode, ', '.join(['\'{}\''.format(s) for s in SUPPORTED_MODES])
    )
    return msg


def _assert_supported_dtype(dtype):
    supported_dtypes = [np.dtype(dt) for dt in SUPPORTED_DTYPES]
    dtype = np.dtype(dtype)  # make sure it is a valid numpy dtype input
    if dtype not in supported_dtypes:
        msg = "Invalid dtype='{}'. Acceptable dtypes are: {}.".format(
            dtype, ', '.join(["'{}'".format(s) for s in supported_dtypes])
        )
        raise ValueError(msg)


def _assert_supported_mode(mode: str):
    if not isinstance(mode, str):
        raise ValueError('Must be a string')
    if mode.lower() not in SUPPORTED_MODES:
        raise ValueError(_err_msg_valid_mode(mode=mode))


def assert_shape_broadcastable(shp0: Sequence[int], shp1: Sequence[int]):
    # TODO(@dperdios): global to pyus?
    if not is_shape_broadcastable(shp0=shp0, shp1=shp1):
        raise ValueError(
            'Arrays with shapes {} and {} are not '
            'broadcastable'.format(shp0, shp1)
        )


def is_broadcastable(a: np.ndarray, b: np.ndarray):
    """Check if arrays `a` and `b` are broadcastable"""
    # TODO(@dperdios): global to pyus?
    return is_shape_broadcastable(a.shape, b.shape)


def is_shape_broadcastable(
        shp0: Sequence[int], shp1: Sequence[int]
) -> bool:
    """Check if shapes `shp0` and `shp1` are broadcastable"""
    # TODO(@dperdios): global to pyus?
    flag = all(
        (m == n) or (m == 1) or (n == 1)
        for m, n in zip(shp0[::-1], shp1[::-1])
    )
    return flag

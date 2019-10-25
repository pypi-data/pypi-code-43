import numpy as np
import collections
from typing import Union, List, Sequence, Tuple, Optional

# Types
Real = Union[int, float]  # TODO: probably np.float and np.float32 etc...
Vector = Union[List[Real], np.ndarray]  # Is it possible to define a np.ndarray[dim=1] for example?
Point = Union[Tuple[Real, Real, Real], List[Real], np.ndarray]

# Checks
_3d_dim = 3


def _assert_3d_point(array: np.ndarray):
    """Assert if `array` is a 3D point"""
    if array.ndim != 1 or array.size != _3d_dim:
        raise ValueError(
            '3D point or vector must be a 1D array of size 3, '
            + msg_current_array_shape(array)
        )


def _assert_3d_point_stack(array: np.ndarray):
    """Assert if `array` is a 3D point stack (i.e. list)"""
    # TODO (@dperdios): add caxis, can be 0, 1 (=-1), maybe link to 3d ND
    if array.ndim != 2 or array.shape[-1] != _3d_dim:
        raise ValueError(
            '3D point or vector stack must be a 2D array of shape '
            '(stack_number, 3), '
            + msg_current_array_shape(array)
        )


def _assert_3d_point_ndarray(array: np.ndarray, caxis: int = -1):
    ndim = array.ndim
    shape = array.shape
    if (caxis < 0 and caxis != -1) and caxis > ndim - 1:
        raise ValueError('Invalid caxis')
    if ndim < 2 or shape[caxis] != _3d_dim:
        expect_shape = [None for _ in range(ndim)]
        expect_shape[caxis] = _3d_dim
        expect_shape = tuple(expect_shape)
        raise ValueError(
            'Invalid ND array of 3D points or vectors'
            'with caxis={}. '.format(caxis)
            + msg_current_array_shape(array).capitalize() + ', '
            + msg_expected_shape(expect_shape)
        )


def _assert_1d_array(array: np.ndarray):
    """Assert if `array` is a 1D array"""
    _assert_nd_array(array=array, ndim=1)


def _assert_2d_array(array: np.ndarray):
    """Assert if `array` is a 2D array"""
    _assert_nd_array(array=array, ndim=2)


def _assert_nd_array(array: np.ndarray, ndim: int):
    """Assert if `array` is a ND array"""
    if array.ndim != ndim:
        raise ValueError(
            'Must be a {}D array, '.format(ndim) + msg_current_array_shape(array)
        )


def _assert_same_len(*xi):
    """Assert if all inputs have the same length"""
    # Try to unpack `*xi` if necessary
    if len(xi) == 1:
        _assert_sequence(xi)
        xi = xi[0]

    len_list = [len(x) for x in xi]
    # Check if all equal in `len_list`
    if not _is_elem_identical(len_list):
        raise ValueError('Must be same length')


def _is_elem_identical(seq: Sequence):
    """Check if all elements in a sequence are identical

    More info:
    https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical#3844948
    """
    _assert_sequence(seq)
    return seq.count(seq[0]) == len(seq)


def _assert_sequence(x):
    """Assert if `x` is not a sequence

    More info:
    https://docs.python.org/3/library/collections.abc.html
    """
    if not isinstance(x, collections.Sequence):
        raise TypeError('Must be iterable')


def _assert_str(x):
    """Assert if `x` is not a string"""
    if not isinstance(x, str):
        raise TypeError('Must be a string')


def msg_incompat_array_shape(
        array: np.ndarray, expected_shape: Sequence,
        name: Optional[str] = None
) -> str:

    if name is not None:
        name = '`{}` array'.format(name)

    msg = (
        'Incompatible {name:} shape. '.format(name=name)
        + msg_current_array_shape(array).capitalize() + ', '
        + msg_expected_shape(expected_shape)
    )

    return msg


def msg_current_array_shape(array: np.ndarray) -> str:
    return 'current shape={shape:}'.format(shape=array.shape)


def msg_expected_shape(shape: Sequence) -> str:
    return 'expected shape={shape:}'.format(shape=shape)


def _assert_int_number(x):
    """Assert if `x` is not integer"""
    valid_type = (int, np.int, np.int32, np.int64)
    if not type(x) in valid_type:
        raise ValueError('Must be an integer')


def _assert_real_number(x):
    """Assert if `x` is not a real number"""
    valid_type = (
        int, float, np.float, np.float32, np.float64, np.int, np.int32,
        np.int64
    )
    if not type(x) in valid_type:
        raise ValueError('Must be a real number')


def _assert_positive_real_number(x):
    """Assert if `x` is not a positive real number"""
    _assert_real_number(x=x)
    if x < 0:
        raise ValueError('Must be a positive real number')


def get_compat_real_dtype(dtype) -> np.dtype:
    """Get compatible real (float) dtype w.r.t. complex-float dtype"""
    dtype = np.dtype(dtype)

    if dtype.kind not in ('f', 'c'):
        ValueError('Invalid dtype. Only supports float and complex-float')

    if dtype.kind == 'c':
        real_dtype_str = 'f{:d}'.format(dtype.itemsize // 2)
        real_dtype = np.dtype(real_dtype_str)
    else:
        real_dtype = dtype

    return real_dtype


def assert_dtype(x: np.ndarray, dtype):
    """Assert if `x.dtype` is not `dtype`"""
    # TODO(@dperdios): will need some tweaking when accepting pycuda.gpuarray
    if x.dtype != dtype:
        raise ValueError('Invalid dtype. Must be {}'.format(dtype))

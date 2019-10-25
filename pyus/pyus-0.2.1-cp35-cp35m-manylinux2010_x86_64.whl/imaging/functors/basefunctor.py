from abc import ABCMeta, abstractmethod

import numpy as np

from pyus.core.cython.imaging.functors.utils import apply_functor
from pyus.utils.types import assert_dtype


class BaseFunctor(metaclass=ABCMeta):
    """Base class for delay-and-sum functors"""
    def __init__(self, dtype):

        self._dtype = np.dtype(dtype)

        # TODO: functor as argument for base class construction?
        self._functor = None

    # Properties
    @property
    def dtype(self):
        return self._dtype

    # Abstract methods
    @abstractmethod
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:
        pass

    # Methods
    def __call__(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        # Check inputs
        #   im_pos(3,1) -> el_pos(3,N)
        #   el_pos(3,1) -> el_pos(3,N)
        self._check_inputs(im_pos=im_pos, el_pos=el_pos)

        return self._call(im_pos=im_pos, el_pos=el_pos)

    def _check_inputs(self, im_pos: np.ndarray, el_pos: np.ndarray):

        # Check dtype
        dtype = self._dtype
        assert_dtype(im_pos, dtype=dtype)
        assert_dtype(el_pos, dtype=dtype)

        # Check 2D arrays (points) -> (3, N)
        # TODO(@dperdios): refactor and use utils.types assertion methods
        if im_pos.ndim != 2:
            raise ValueError('Wrong dimension number. Must be a 2D array')
        if el_pos.ndim != 2:
            raise ValueError('Wrong dimension number. Must be a 2D array')
        im_pos_shape = im_pos.shape
        el_pos_shape = el_pos.shape
        if im_pos_shape[0] != 3:
            raise ValueError('Wrong shape. Must be (3, N)')
        if el_pos_shape[0] != 3:
            raise ValueError('Wrong shape. Must be (3, N)')

        # Check compatible shapes
        #   im_pos(3,1) -> el_pos(3,N)
        #   el_pos(3,1) -> el_pos(3,N)
        #   TODO(@dperdios): im_pos(3, N) with el_pos(3, N)
        if im_pos_shape[1] > 1 and el_pos_shape[1] > 1:
            raise ValueError('Incompatible shapes')

    # Note: this method is here only for test purposes and should not be called
    # otherwise
    def _cy_call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        # Check inputs
        self._check_inputs(im_pos=im_pos, el_pos=el_pos)

        # Squeeze to fit the `apply_functor` buffer expectation, i.e. one of
        # the two inputs should be should be (3,) the other (3,N)
        im_pos = np.squeeze(im_pos)
        el_pos = np.squeeze(el_pos)

        return apply_functor(im_pos, el_pos, self._functor)

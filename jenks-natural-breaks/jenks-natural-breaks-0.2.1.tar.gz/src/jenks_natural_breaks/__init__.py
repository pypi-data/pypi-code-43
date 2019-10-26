__version__ = '0.2.1'

import numpy as np

from ._jenks_matrices import ffi as _ffi
from ._jenks_matrices import lib as _lib


def _jenks_matrices(data, n_classes):
    lower_class_limits = np.zeros((len(data) + 1, n_classes + 1), dtype=np.uint32)
    variance_combinations = np.zeros((len(data) + 1, n_classes + 1), dtype=np.float64)

    lower_class_limits[1, 1:] = 1
    variance_combinations[2:, 1:] = float("inf")

    _lib.jenks_matrices(
        len(data), n_classes,
        _ffi.cast("double *", data.ctypes.data),
        _ffi.cast("unsigned int *", lower_class_limits.ctypes.data),
        _ffi.cast("double *", variance_combinations.ctypes.data))

    return lower_class_limits, variance_combinations


def _jenks_breaks(data, lower_class_limits, n_classes):
    class_breaks = [data[-1]] * (n_classes + 1)
    k = len(data)
    for i in range(n_classes, 0, -1):
        k = max(0, lower_class_limits[k, i] - 1)
        class_breaks[i - 1] = data[k]

    return class_breaks


def classify(data, n_classes):
    assert len(data.shape) == 1 and n_classes <= data.shape[0]
    data = data.astype(np.float64)
    data.sort()
    lower_class_limits, _ = _jenks_matrices(data, n_classes)
    return _jenks_breaks(data, lower_class_limits, n_classes)

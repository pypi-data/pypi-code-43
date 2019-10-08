#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import threading
import numpy as np
from .spline import Spline
from . import _decor


class Distortion:
    def __init__(self):
        self._dist = None
        self._lock = threading.Lock()
        self.spline = None
        self.spline_file = None
        self.shape = None
        self._spline_checksum = 0

    def init(self, spline):
        with self._lock:
            if spline:
                checksum = binascii.crc32(spline.encode())
                res = checksum == self._spline_checksum
                self._spline_checksum = checksum
                if not res:
                    self.spline_file = spline
                    self.spline = Spline(spline)
                    self._dist = None
            else:
                self._spline_checksum = 0
                self._dist = None
                self.shape = None
                self.spline_file = None
                self.spline = None

    def __call__(self, image):
        return self._correct(image if isinstance(image, np.ndarray) else image.array)

    def _correct(self, image):
        with self._lock:
            if image.shape != self.shape:
                self.shape = image.shape
                self._dist = None
            if self.spline and not self._dist:
                self._init_lut()
        if not self._dist:
            return image
        return np.asarray(_decor._distortion_cor(self._dist, np.ascontiguousarray(image.astype(np.float64))))

    def calc_cartesian_positions(self, d1, d2):
        dx = np.ascontiguousarray(self.spline.func_x_y(0, d1, d2))
        dy = np.ascontiguousarray(self.spline.func_x_y(1, d1, d2))
        return dx, dy

    def _init_lut(self):
        dim1, dim2 = self.shape
        d1 = dim1 + 1
        d2 = dim1 + 1
        dx, dy = self.calc_cartesian_positions(d1, d2)
        self._dist = _decor._distortion(dim1, dim2, dx, dy)

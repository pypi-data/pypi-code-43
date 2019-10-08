#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from . import _decor


class Spline(object):
    len_float_str = 14  # by default one float is 14 char in ascii

    def __init__(self, filename):
        self.filename = filename
        self._parse()

    def _parse(self):
        with open(self.filename) as file:
            string_spline = [i.rstrip() for i in file]
        index_line = 0
        for oneLine in string_spline:
            striped_line = oneLine.strip().upper()
            if striped_line == 'VALID REGION':
                data = string_spline[index_line + 1]
                self.xmin = float(data[self.len_float_str * 0:self.len_float_str * 1])
                self.ymin = float(data[self.len_float_str * 1:self.len_float_str * 2])
                self.xmax = float(data[self.len_float_str * 2:self.len_float_str * 3])
                self.ymax = float(data[self.len_float_str * 3:self.len_float_str * 4])
            elif striped_line == 'GRID SPACING, X-PIXEL SIZE, Y-PIXEL SIZE':
                data = string_spline[index_line + 1]
                self.grid = float(data[:self.len_float_str])
                self.pixel_size = (
                    float(data[self.len_float_str:self.len_float_str * 2]),
                    float(data[self.len_float_str * 2:self.len_float_str * 3])
                )
            elif striped_line == 'X-DISTORTION':
                data = string_spline[index_line + 1]
                spline_knots_x_len, spline_knots_y_len = [int(i) for i in data.split()]
                databloc = []
                for line in string_spline[index_line + 2:]:
                    if len(line) > 0:
                        for i in range(len(line) // self.len_float_str):
                            databloc.append(float(line[i * self.len_float_str: (i + 1) * self.len_float_str]))
                    else:
                        break
                self.x_knots_x = np.array(databloc[:spline_knots_x_len], dtype=np.float64)
                self.x_knots_y = np.array(databloc[spline_knots_x_len:spline_knots_x_len + spline_knots_y_len],
                                          dtype=np.float64)
                self.x_coeff = np.array(databloc[spline_knots_x_len + spline_knots_y_len:], dtype=np.float64)
            elif striped_line == 'Y-DISTORTION':
                data = string_spline[index_line + 1]
                spline_knots_x_len, spline_knots_y_len = [int(i) for i in data.split()]
                databloc = []
                for line in string_spline[index_line + 2:]:
                    if len(line) > 0:
                        for i in range(len(line) // self.len_float_str):
                            databloc.append(float(line[i * self.len_float_str:(i + 1) * self.len_float_str]))
                    else:
                        break
                self.y_knots_x = np.array(databloc[:spline_knots_x_len], dtype=np.float64)
                self.y_knots_y = np.array(databloc[spline_knots_x_len:spline_knots_x_len + spline_knots_y_len],
                                          dtype=np.float64)
                self.y_coeff = np.array(databloc[spline_knots_x_len + spline_knots_y_len:], dtype=np.float64)
            index_line += 1

    def func_x_y(self, r, dim1, dim2):
        res = np.zeros((dim1 * dim2,), dtype=np.double)
        if r == 0:
            _decor._bispev(self.x_knots_x, self.x_knots_y, self.x_coeff, dim1, dim2, res, 0)
        else:
            _decor._bispev(self.y_knots_x, self.y_knots_y, self.y_coeff, dim1, dim2, res, 1)
        return res

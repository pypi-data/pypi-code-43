# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from skimage.measure import compare_ssim as ssim

__author__ = "Daniel Scheffler"


def calc_ssim(image0, image1, dynamic_range=None, win_size=None, gaussian_weights=False):
    """Calculates Mean Structural Similarity Index between two images.

    :param image0:
    :param image1:
    :param dynamic_range:
    :param win_size:
    :param gaussian_weights:
    :return:
    """
    if image0.dtype != image1.dtype:
        image0 = image0.astype(np.int16)
        image1 = image1.astype(np.int16)

    return ssim(image0, image1, data_range=dynamic_range, win_size=win_size, gaussian_weights=gaussian_weights)

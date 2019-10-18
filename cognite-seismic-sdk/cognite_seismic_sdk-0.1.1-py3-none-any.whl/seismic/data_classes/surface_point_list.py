# Copyright 2019 Cognite AS

import itertools

import numpy as np


class SurfacePointList(list):
    def to_array(self):
        new_list = [list(g) for k, g in itertools.groupby(self, lambda x: x.iline)]
        result = []
        for inline_group in new_list:
            result.append(np.array([i.value for i in inline_group]))

        return np.array(result)

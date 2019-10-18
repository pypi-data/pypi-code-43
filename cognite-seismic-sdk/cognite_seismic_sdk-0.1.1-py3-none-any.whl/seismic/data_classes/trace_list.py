# Copyright 2019 Cognite AS

import itertools

import numpy as np


class Trace3DList(list):
    def to_array(self):
        new_list = [list(g) for k, g in itertools.groupby(self, lambda x: x.iline.value)]
        result = []
        for inline_group in new_list:
            result.append(np.array([np.array(i.trace) for i in inline_group]))
        return np.array(result)


class Trace2DList(list):
    def to_array(self):
        return np.array([np.array(t.trace) for t in self])

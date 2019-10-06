"""
   Copyright 2019 Riley John Murray

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from itertools import product
from collections import defaultdict
import numpy as np
import scipy.sparse as sp

__REAL_TYPES__ = (int, float, np.int_, np.float_, np.longdouble)


def zero_func():
    return 0


def array_index_iterator(shape):
    return product(*[range(d) for d in shape])


def sparse_matrix_data_to_csc(data_tuples, index_map=None):
    """
    Parameters
    ----------
    data_tuples : a list of tuples
        Each tuple is of the form ``(A_vals, A_rows, A_cols, len)``, where ``A_vals`` is a
        list, ``A_rows`` is a 1d numpy array, ``A_cols`` is a list, and ``len`` is the number
        of rows in the matrix block specified by this tuple.
    index_map : dict
        If provided, will map ScalarVariable ids to columns of the returned sparse matrix.
        If none, this function computes and returns an appropriate value for index_map which
        eliminates all unnecessary ScalarVariables.

    Returns
    -------
    (A, index_map) - a tuple (CSC matrix, dict)
        ``A`` is the sparse matrix formed by concatenating the various CSC matrices
        specified by the quadruplets in ``data_tuples``, and dropping / reindexing rows
         per ``index_map``.
    """
    # d in data_tuples is length 4, and has the following format:
    #   d[0] = A_vals, a list
    #   d[1] = A_rows, a 1d numpy array
    #   d[2] = A_cols, a list
    #   d[3] = the number of rows of this matrix block
    A_cols = []
    A_vals = []
    row_index_offset = 0
    for A_v, A_r, A_c, num_rows in data_tuples:
        A_r[:] += row_index_offset
        A_cols += A_c
        A_vals += A_v
        row_index_offset += num_rows
    A_rows = np.hstack([d[1] for d in data_tuples]).astype(int)
    if index_map is None:
        unique_cols = np.sort(np.unique(A_cols))
        index_map = defaultdict(lambda: -1)
        index_map.update({c: idx for (idx, c) in enumerate(unique_cols)})
        num_cols = unique_cols.size
        # We convert to a defaultdict with dummy value.
        # The dummy value is used to assign values to ScalarVariable objects
        # whose parent Variable participates in an optimization problem,
        # even when the ScalarVariable itself does not appear in the problem.
    else:
        num_cols = max(index_map.values()) + 1
    A_cols = np.array([index_map[ac] for ac in A_cols])
    num_rows = np.max(A_rows) + 1
    A = sp.csc_matrix((A_vals, (A_rows, A_cols)),
                      shape=(int(num_rows), int(num_cols)), dtype=float)
    return A, index_map


def parse_cones(K):
    """
    :param K: a list of Cones

    :return: a map from cone type to indices for (A,b) in the conic system
    {x : A @ x + b \in K}, and from cone type to a 1darray of cone lengths.
    """
    m = sum(co.len for co in K)
    type_selectors = defaultdict(lambda: (lambda: np.zeros(shape=(m,), dtype=bool))())
    type_to_cone_start_stops = defaultdict(lambda: list())
    running_idx = 0
    for i, co in enumerate(K):
        type_selectors[co.type][running_idx:(running_idx+co.len)] = True
        type_to_cone_start_stops[co.type] += [(running_idx, running_idx + co.len)]
        running_idx += co.len
    return type_selectors, type_to_cone_start_stops


def sparse_matrix_is_diag(A):
    nonzero_row_idxs, nonzero_col_idxs = A.nonzero()
    nonzero_col_idxs = np.unique(nonzero_col_idxs)
    nonzero_row_idxs = np.unique(nonzero_row_idxs)
    return A.nnz == A.shape[0] and len(nonzero_col_idxs) == len(nonzero_row_idxs)

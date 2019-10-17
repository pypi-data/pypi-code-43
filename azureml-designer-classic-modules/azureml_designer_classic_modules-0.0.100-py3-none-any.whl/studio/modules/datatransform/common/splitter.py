import itertools
import numpy as np
from typing import List

from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.logger import module_logger as logger
from azureml.studio.common.error import ErrorMapping


def stratify_split_to_indices_groups(table: DataTable, strats_column: DataTableColumnSelection):
    """
    :param table: Input dataTable.
    :param strats_column: key column selector, only support single column.
    :return: A list of list<int>, each element indicates a set of row indices for the same group.
    """

    # check if strats_column select at least 1 column.
    strats_column_indices = strats_column.select_column_indexes(table)
    ErrorMapping.verify_are_columns_selected(curr_selected_num=len(strats_column_indices),
                                             required_selected_num=1,
                                             arg_name="strats_column")
    key_index = strats_column_indices[0]
    key_name = table.get_column_name(key_index)
    df = table.data_frame

    logger.info(f"stratify table by column '{key_name}'")
    # first, we extract all rows with null value into one group.
    # returns a series of True/False value indicates if each row has a null(None/NaN) value in key column.

    rows_with_null = df[key_name].isnull()
    # split table with the flag series.
    idx_of_null_rows = rows_with_null[rows_with_null].index
    column_without_null = df[key_name][~rows_with_null]

    # stratify non-null rows by key column.
    groups = column_without_null.groupby(column_without_null)
    indices_groups = [list(index) for key, index in groups.indices.items()]
    if len(idx_of_null_rows) > 0:
        indices_groups.append(list(idx_of_null_rows))
    return indices_groups


def split(
        index_array: List[int],
        fold_elem_count: List[int],
        rand: np.random.RandomState = None,
        with_replacement: bool = False):
    """
    :param index_array: A list of row indices to split.
    :param fold_elem_count: A list contains the element count of per fold.
    :param rand: If provided, index_array will be shuffled with random state before splitting.
    :param with_replacement: This option is used for 'Partition and Sample' Module.
        Pass 'True' if you want the sampled row to be put back into the pool of rows for potential
        reuse. As a result, the same row might be assigned to several folds.
        If you do not use replacement (default as 'False'), the sampled row is not put back into the pool of rows for
        potential reuse. As a result, each row can be assigned to only one fold.
    :return:
    """
    if rand and with_replacement:
        index_split = []
        for fold_cnt in fold_elem_count:
            rand.shuffle(index_array)
            index_split.append(index_array[0:fold_cnt])
    else:
        if rand:
            rand.shuffle(index_array)
        """
        example:
            fold_elem_count = [3, 5, 7]
            end_indices = [3, 8, 15]
            start_indices = [0, 3, 8, 15]
            zip(start_indices, end_indices) = [(0,3), (3,8), (8,15)]
        """
        end_indices = list(itertools.accumulate(fold_elem_count))
        start_indices = [0] + end_indices
        index_split = [index_array[a:b] for a, b in zip(start_indices, end_indices)]

    return index_split

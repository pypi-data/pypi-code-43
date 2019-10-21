import pandas as pd
import numpy as np
import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from ..remove_duplicate_rows import RemoveDuplicateRowsModule


@pytest.fixture
def input_data_table():
    df = pd.DataFrame(
        data=np.array([
            [1, 1, 1, 1],
            [1, 1, 1, 2],
            [1, 1, 2, 3],
            [1, 1, 2, 4],
            [1, 2, 3, 5],
            [1, 2, 3, 6],
            [1, 2, 4, 7],
            [1, 2, 4, 8],
            [2, 1, 1, 9],
            [2, 1, 1, 10],
            [2, 1, 2, 11],
            [2, 1, 2, 12],
            [2, 2, 3, 13],
            [2, 2, 3, 14],
            [2, 2, 4, 15],
            [2, 2, 4, 16],
        ]),
        columns=['A', 'B', 'C', 'D']
    )
    return DataTable(df)


@pytest.fixture
def input_data_table_with_missing():
    df = pd.DataFrame(
        data=np.array([
            [1, 1, 1, 1],
            [1, 1, 1, 2],
            [np.nan, 1, 1, 3],
            [np.nan, 1, 1, 4],
            [1, np.nan, 3, 5],
            [1, np.nan, 3, 6],
            [1, 2, 4, 7],
            [1, 2, 4, 8],
        ]),
        columns=['A', 'B', 'C', 'D']
    )
    return DataTable(df)


@pytest.fixture
def input_data_table_with_missing_large():
    df = pd.DataFrame(
        data=np.array([
            [1, 1, 1, 1],
            [1, 1, 1, 2],
            [np.nan, 1, 1, 3],
            [np.nan, 1, 1, 4],
            [1, np.nan, 3, 5],
            [1, np.nan, 3, 6],
            [1, 2, 4, 7],
            [1, 2, 4, 8],
        ]*50000),
        columns=['A', 'B', 'C', 'D']
    )
    return DataTable(df)


@pytest.fixture
def input_data_table_one_row():
    df = pd.DataFrame(
        data=np.array([
            [1, 1, 1, 1],
        ]),
        columns=['A', 'B', 'C', 'D']
    )
    return DataTable(df)


@pytest.fixture
def column_selection_a():
    return DataTableColumnSelection('''
{
  "isFilter":true,
  "rules": [
    {"ruleType":"ColumnNames", "columns":["A"], "exclude":false}
  ]
}''')


@pytest.fixture
def column_selection_ab():
    return DataTableColumnSelection('''
{
  "isFilter":true,
  "rules": [
    {"ruleType":"ColumnNames", "columns":["A", "B"], "exclude":false}
  ]
}''')


@pytest.fixture
def column_selection_abc():
    return DataTableColumnSelection('''
{
  "isFilter":true,
  "rules": [
    {"ruleType":"ColumnNames", "columns":["A", "B", "C"], "exclude":false}
  ]
}''')


def test_success_remove_dup_rows_a_first(input_data_table, column_selection_a):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_a,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[0, 8]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_a_last(input_data_table, column_selection_a):
    take_first = False
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_a,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[7, 15]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_ab_first(input_data_table, column_selection_ab):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_ab,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[0, 4, 8, 12]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_ab_last(input_data_table, column_selection_ab):
    take_first = False
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_ab,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[3, 7, 11, 15]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_abc_first(input_data_table, column_selection_abc):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_abc,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[0, 2, 4, 6, 8, 10, 12, 14]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_abc_last(input_data_table, column_selection_abc):
    take_first = False
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table,
        key_columns=column_selection_abc,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table.data_frame.iloc[[1, 3, 5, 7, 9, 11, 13, 15]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_a_first_with_nan(input_data_table_with_missing, column_selection_abc):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table_with_missing,
        key_columns=column_selection_abc,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table_with_missing.data_frame.iloc[[0, 2, 3, 4, 5, 6]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_a_last_with_nan(input_data_table_with_missing, column_selection_abc):
    take_first = False
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table_with_missing,
        key_columns=column_selection_abc,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table_with_missing.data_frame.iloc[[1, 2, 3, 4, 5, 7]].reset_index(drop=True)
    assert (result.data_frame.equals(expect_result))


def test_success_remove_dup_rows_a_first_with_nan_large(input_data_table_with_missing_large, column_selection_abc):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table_with_missing_large,
        key_columns=column_selection_abc,
        take_first_otherwise_last=take_first)[0]
    assert result.number_of_rows == 200002


def test_success_remove_dup_rows_a_one_row(input_data_table_one_row, column_selection_a):
    take_first = True
    result = RemoveDuplicateRowsModule.run(
        data_table=input_data_table_one_row,
        key_columns=column_selection_a,
        take_first_otherwise_last=take_first)[0]
    expect_result = input_data_table_one_row
    assert (result.data_frame.equals(expect_result.data_frame))
    # check if return a cloned table
    assert result is not expect_result

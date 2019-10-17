import os

import numpy as np
import pandas as pd
import pytest

from azureml.studio.core.utils.column_selection import ColumnType
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import InvalidColumnTypeError
from azureml.studio.modules.datatransform.scale_and_reduce.normalize_data.nomalize_transformer import \
    TransformationMethods
from ..normalize_data import NormalizeDataModule


@pytest.fixture
def data_table():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


@pytest.fixture
def zscored_dt():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'Zscored_dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


@pytest.fixture
def lognormaled_dt():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'lognormaled_dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


@pytest.fixture
def min_max_dt():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'min_max_dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


@pytest.fixture
def logistic_dt():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'logistic_dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


@pytest.fixture
def tanh_dt():
    file_path = os.path.join(r'azureml/studio/tests/integration/input/module_invoking/normalize_data/',
                             'tanh_dataset.csv')
    dt = DataTable(pd.read_csv(file_path))
    return dt


def complex_data_table():
    df = pd.DataFrame()
    df['int'] = [2, 1, 10]
    df['float'] = [np.nan, 1.6, 1]
    df['str'] = [np.nan, 'a', 'b']
    df['bool'] = [None, True, False]
    df['category'] = pd.Series([np.nan, 'c', 'f']).astype('category')
    df['datetime'] = pd.to_datetime(
        arg=pd.Series([np.nan, '20190129', np.nan]), format='%Y%m%d', errors='coerce')
    df['timedelta'] = pd.to_timedelta(
        arg=pd.Series([np.nan, 30, 'c']), unit='d', errors='coerce')
    return DataTable(df)


@pytest.fixture
def column_selection():
    csb = DataTableColumnSelectionBuilder()
    column_selection_number = csb.include_col_types(ColumnType.NUMERIC).build()
    return column_selection_number


def test_zscore(data_table: DataTable, zscored_dt, column_selection):
    out = NormalizeDataModule.run(
        data_set=data_table,
        method=TransformationMethods.ZScore,
        column_set=column_selection,
        constant_column_option=True)
    our_result = out[0]
    indexs = column_selection.select_column_indexes(data_table)
    num_names = [data_table.get_column_name(index) for index in indexs]
    for column_name in data_table.column_names:
        our_column = our_result.get_column(column_name)
        ref_column = zscored_dt.get_column(column_name)
        if column_name in num_names:
            assert np.allclose(our_column, ref_column, equal_nan=True)
        else:
            assert all((our_column == ref_column) | ((our_column.isna()) & (ref_column.isna())))


def test_lognormal(data_table: DataTable, lognormaled_dt, column_selection):
    out = NormalizeDataModule.run(
        data_set=data_table,
        method=TransformationMethods.LogNormal,
        column_set=column_selection,
        constant_column_option=True)
    our_result = out[0]
    indexs = column_selection.select_column_indexes(data_table)
    num_names = [data_table.get_column_name(index) for index in indexs]
    for column_name in data_table.column_names:
        our_column = our_result.get_column(column_name)
        ref_column = lognormaled_dt.get_column(column_name)
        if column_name in num_names:
            assert np.allclose(our_column, ref_column, equal_nan=True)
        else:
            assert all((our_column == ref_column) | ((our_column.isna()) & (ref_column.isna())))


def test_min_max(data_table: DataTable, min_max_dt, column_selection):
    out = NormalizeDataModule.run(
        data_set=data_table,
        method=TransformationMethods.MinMax,
        column_set=column_selection,
        constant_column_option=True)
    our_result = out[0]
    indexs = column_selection.select_column_indexes(data_table)
    num_names = [data_table.get_column_name(index) for index in indexs]
    for column_name in data_table.column_names:
        our_column = our_result.get_column(column_name)
        ref_column = min_max_dt.get_column(column_name)
        if column_name in num_names:
            assert np.allclose(our_column, ref_column, equal_nan=True)
        else:
            assert all((our_column == ref_column) | ((our_column.isna()) & (ref_column.isna())))


def test_logistic(data_table: DataTable, logistic_dt, column_selection):
    out = NormalizeDataModule.run(
        data_set=data_table,
        method=TransformationMethods.Logistic,
        column_set=column_selection,
        constant_column_option=True)
    our_result = out[0]
    indexs = column_selection.select_column_indexes(data_table)
    num_names = [data_table.get_column_name(index) for index in indexs]
    for column_name in data_table.column_names:
        our_column = our_result.get_column(column_name)
        ref_column = logistic_dt.get_column(column_name)
        if column_name in num_names:
            assert np.allclose(our_column, ref_column, equal_nan=True)
        else:
            assert all((our_column == ref_column) | ((our_column.isna()) & (ref_column.isna())))


def test_tanh(data_table: DataTable, tanh_dt, column_selection):
    out = NormalizeDataModule.run(
        data_set=data_table,
        method=TransformationMethods.Tanh,
        column_set=column_selection,
        constant_column_option=True)
    our_result = out[0]
    indexs = column_selection.select_column_indexes(data_table)
    num_names = [data_table.get_column_name(index) for index in indexs]
    for column_name in data_table.column_names:
        our_column = our_result.get_column(column_name)
        ref_column = tanh_dt.get_column(column_name)
        if column_name in num_names:
            assert np.allclose(our_column, ref_column, equal_nan=True)
        else:
            assert all((our_column == ref_column) | ((our_column.isna()) & (ref_column.isna())))


@pytest.mark.parametrize(
    'exclude_column_type, illegal_column_names',
    [
        (ColumnType.STRING, ['bool', 'category', 'datetime', 'timedelta']),
        (ColumnType.INTEGER, ['str', 'bool', 'category', 'datetime', 'timedelta']),
        (ColumnType.DOUBLE, ['str', 'bool', 'category', 'datetime', 'timedelta']),
        (ColumnType.BOOLEAN, ['str', 'category', 'datetime', 'timedelta']),
        (ColumnType.DATETIME, ['str', 'bool', 'category', 'timedelta']),
        (ColumnType.TIME_SPAN, ['str', 'bool', 'category', 'datetime']),
        (ColumnType.CATEGORICAL, ['str', 'bool', 'datetime', 'timedelta']),
        (ColumnType.NUMERIC, ['str', 'bool', 'category', 'datetime', 'timedelta'])
    ]
)
def test_receive_not_numeric_column(exclude_column_type, illegal_column_names):
    data_table = complex_data_table()
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().exclude_col_types(exclude_column_type).build()
    with pytest.raises(
            expected_exception=InvalidColumnTypeError,
            match=f'Cannot process column "{",".join(illegal_column_names)}" of type.'):
        _ = NormalizeDataModule.run(
            data_set=data_table,
            method=TransformationMethods.Logistic,
            column_set=column_selection,
            constant_column_option=True)

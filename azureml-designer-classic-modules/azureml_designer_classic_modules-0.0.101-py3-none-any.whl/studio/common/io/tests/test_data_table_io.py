import os

import pandas as pd
import numpy as np
import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.io.data_table_io import read_data_table, write_data_table
from azureml.studio.common.io.pickle_utils import read_with_pickle_from_file
from azureml.studio.core.utils.fileutils import ensure_folder
from azureml.studio.core.utils.strutils import generate_random_string


@pytest.fixture
def input_data_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))


@pytest.fixture
def input_data_table_multi_types():
    df = pd.DataFrame()
    df['int'] = [1, 10, np.nan]
    df['float'] = [1.6, 1, np.nan]
    df['string'] = ['3', '1', np.nan]
    df['bool'] = [True, np.nan, False]
    df['category'] = pd.Series([2, 1, 3]).astype('category')
    df['datetime'] = pd.to_datetime(
        arg=pd.Series(['20190101', '20190103', np.nan]), format='%Y%m%d', errors='coerce')
    df['nan'] = [np.nan, np.nan, np.nan]
    return DataTable(df)


def test_data_table_io(tmpdir, input_data_table_1):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "A"}

    temp_file = generate_random_string()
    dataset_file_name = str(tmpdir.join(f"{temp_file}.dataset.parquet"))
    write_data_table(input_data_table_1, dataset_file_name)
    output_data_table = read_data_table(dataset_file_name)

    assert output_data_table.meta_data.score_column_names == input_data_table_1.meta_data.score_column_names
    assert output_data_table.data_frame.equals(input_data_table_1.data_frame)


def test_data_table_multi_types(tmpdir, input_data_table_multi_types):
    temp_file = generate_random_string()
    dataset_file_name = str(tmpdir.join(f"{temp_file}.dataset.parquet"))
    write_data_table(input_data_table_multi_types, dataset_file_name)
    output_data_table = read_data_table(dataset_file_name)
    assert output_data_table.data_frame.equals(input_data_table_multi_types.data_frame)
    assert output_data_table.meta_data.column_attributes == input_data_table_multi_types.meta_data.column_attributes


def test_write_zero_row_data_table():
    zero_row_data_table = DataTable(pd.DataFrame(columns=['col0', 'col1', 'col2']))
    output_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gen')
    ensure_folder(output_folder)
    output_file_name = os.path.join(output_folder, 'zero_row_data_table.dataset.parquet')
    write_data_table(zero_row_data_table, output_file_name)
    assert os.path.isfile(output_file_name)
    assert os.path.isfile(output_file_name.replace('.parquet', ''))


def test_read_empty_data_table():
    input_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input', 'empty_data_table.dataset.parquet')
    dt = read_data_table(input_file_path)
    assert dt.data_frame.equals(pd.DataFrame())
    assert dt.meta_data.column_attributes == DataTable(pd.DataFrame()).meta_data.column_attributes


def test_read_zero_row_data_table():
    input_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input', 'zero_row_data_table.dataset.parquet')
    dt = read_data_table(input_file_path)
    assert dt.data_frame.equals(pd.DataFrame(columns=['col0', 'col1', 'col2']))


def test_read_data_table_from_only_parquet_file():
    input_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input', 'data.dataset.parquet')
    dt = read_data_table(input_file_path)
    assert dt

    # Assert meta data is recovered from parquet file
    expect_meta_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input', 'meta_data.dataset')
    expect_meta_data = read_with_pickle_from_file(expect_meta_file)
    assert dt.meta_data.column_attributes == expect_meta_data.column_attributes


def test_missing_both_meta_data_file_and_parquet_file():
    input_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input', 'dummy.dataset.parquet')
    with pytest.raises(
        FileNotFoundError,
        match=r'Both meta data file .* and parquet file .* are not found'
    ):
        read_data_table(input_file_path)


def test_ns_precision_datetime_to_parquet(tmp_path):
    # Create series in nanoseconds
    original_series = pd.Series(pd.date_range('2019-8-2 18:50:50', periods=1000, freq='ns'))
    dt = DataTable(pd.DataFrame({'datetime': original_series.astype('datetime64[ns]')}))
    # Ensure the datetime with nanosecond precision can be written.
    path = os.path.join(tmp_path, 'datetime.dataset.parquet')
    write_data_table(dt, path)
    new_dt = read_data_table(path)
    # Ensure the data is the same in ms precision
    assert all(new_dt.data_frame['datetime'] == original_series.astype('datetime64[ms]'))


@pytest.mark.parametrize(
    'mixed_type_name, series, expected_series,',
    [
        ('bool_float', [False, True, 1.2, 1.3, 1.4], [0.0, 1.0, 1.2, 1.3, 1.4]),
        ('bool_int', [False, True, 1, 2, 3], [0, 1, 1, 2, 3]),
        ('bool_str', [False, True, 'aaa', 'bbb'], ['False', 'True', 'aaa', 'bbb']),
        ('bool_int_float', [False, True, 1, 2, 3, 1.5, 1e23], [0.0, 1.0, 1.0, 2.0, 3.0, 1.5, 1e23]),
        ('bool_int_float_str',
         [False, True, 1, 2, 1.5, 1e23, 'aaa'],
         ['False', 'True', '1', '2', '1.5', '1e+23', 'aaa'],
         ),
        ('int_str', [1, 2, 3, 'a', 'b', 'c'], ['1', '2', '3', 'a', 'b', 'c']),
        ('none_str', [None, None, 'a', 'b', 'c'], [None, None, 'a', 'b', 'c']),
        ('none_bool', [None, None, True, False], [None, None, True, False]),
        ('none_bool_str', [None, True, False, 'a'], [None, 'True', 'False', 'a']),
        ('nan_str', [np.nan, True, pd.NaT, 'a', 'b', 'c'], [None, 'True', None, 'a', 'b', 'c']),
        ('nan_bool', [np.nan, True, pd.NaT, True, False], [None, True, None, True, False]),
        ('nan_bool_str', [np.nan, True, pd.NaT, True, False, 'a'], [None, 'True', None, 'True', 'False', 'a']),
        ('nan_bool_float', [np.nan, True, 1.2], [np.nan, 1.0, 1.2]),

        # The following cases will fail since the column type is detected as int,
        # but it be read as float and cause a meta AttributesAndDataframeNotMatchError.
        # ('nat_int', [pd.NaT, 123, 456, 789], [None, 123, 456, 789]),
        # ('nan_bool_int', [np.nan, True, 123, 456, 789], [None, 1, 123, 456, 789]),

        # The following case will fail since the datatable try to convert NaT to float and fail.
        # ('nat_float', [pd.NaT, 1.0, 1.1], [None, 1.0, 1.1]),

    ]
)
def test_mixed_type_write_read(mixed_type_name, series, expected_series, tmp_path):
    key = 'data'
    file_name = 'data.dataset.parquet'
    full_path = os.path.join(tmp_path, file_name)
    dt = DataTable(pd.DataFrame({key: series}))
    expected_dt = DataTable(pd.DataFrame({key: expected_series}))
    write_data_table(dt, full_path)
    loaded_dt = read_data_table(full_path)
    for reload_val, expected_val in zip(loaded_dt.get_column(key), expected_dt.get_column(key)):
        if isinstance(expected_val, float) and np.isnan(expected_val):
            assert np.isnan(reload_val)
        else:
            assert reload_val == expected_val

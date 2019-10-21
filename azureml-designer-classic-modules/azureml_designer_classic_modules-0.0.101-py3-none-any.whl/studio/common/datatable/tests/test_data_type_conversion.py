import pytest

import numpy as np
import pandas as pd

from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.common.datatable.data_type_conversion import convert_column_by_element_type, \
    convert_scalar_by_element_type, _drop_na_and_convert
from azureml.studio.common.utils.datetimeutils import convert_to_datetime, convert_to_time_span
from azureml.studio.common.datatable.constants import ElementTypeName


@pytest.fixture
def data_frame():
    df = pd.DataFrame()
    df['col0'] = [2, 1, 10]
    df['col1'] = [np.nan, 1.6, 1]
    df['col2'] = [np.nan, 'a', 'b']
    df['col3'] = [None, True, False]
    df['col4'] = pd.Series([np.nan, 'c', 'f']).astype('category')
    df['col5'] = pd.to_datetime(
        arg=pd.Series([np.nan, '20190129', np.nan]), format='%Y%m%d', errors='coerce')
    df['col6'] = pd.to_timedelta(
        arg=pd.Series([np.nan, 30, 'c']), unit='d', errors='coerce')
    return df


"""
Test function convert_column_by_element_type, target type is ElementTypeName.INT
"""


def test_convert_column_by_element_type_int_to_int(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 0], ElementTypeName.INT)
    expect_column = pd.Series([2, 1, 10])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.INT


def test_convert_column_by_element_type_float_to_int(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 1], ElementTypeName.INT)
    expect_column = pd.Series([np.nan, 1, 1])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_string_to_int(data_frame):
    input_column = pd.Series([None, '1', '10'])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    expect_column = pd.Series([np.nan, 1.0, 10.0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT

    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.INT}":'):
        convert_column_by_element_type(data_frame.iloc[:, 2], ElementTypeName.INT)


def test_convert_column_by_element_type_bool_to_int(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 3], ElementTypeName.INT)
    expect_column = pd.Series([np.nan, 1, 0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_datetime_to_int():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    expect_column = pd.Series(1548720000)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.INT


def test_convert_column_by_element_type_timespan_to_int():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    expect_column = pd.Series(432000)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.INT


def test_convert_column_by_element_type_category_to_int():
    input_column = pd.Series([1, 2, 3], dtype='category')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    expect_column = pd.Series([1, 2, 3])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.INT


def test_convert_column_by_element_type_nan_to_int():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.FLOAT
"""


def test_convert_column_by_element_type_int_to_float(data_frame):
    input_column = data_frame.iloc[:, 0]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series([2.0, 1.0, 10.0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_float_to_float(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series([np.nan, 1.6, 1.0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_string_to_float(data_frame):
    input_column = pd.Series([None, '1.0', '10.0'])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series([np.nan, 1.0, 10.0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT

    input_column = data_frame.iloc[:, 2]
    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.FLOAT}":'):
        convert_column_by_element_type(input_column, ElementTypeName.FLOAT)


def test_convert_column_by_element_type_bool_to_float(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 3], ElementTypeName.FLOAT)
    expect_column = pd.Series([None, 1.0, 0.0], dtype='float64')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_category_to_float():
    input_column = pd.Series([None, np.nan, 3], dtype='category')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series([np.nan, np.nan, 3.0])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_datetime_to_float():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series(1548720000.0)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_timespan_to_float():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.FLOAT)
    expect_column = pd.Series(432000.0)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.FLOAT


def test_convert_column_by_element_type_nan_to_float():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.STRING
"""


def test_convert_column_by_element_type_int_to_string(data_frame):
    input_column = pd.Series([np.nan, 1, 2])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series([np.nan, '1.0', '2.0'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_float_to_string(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series([np.nan, '1.6', '1.0'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_string_to_string(data_frame):
    input_column = data_frame.iloc[:, 2]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series([np.nan, 'a', 'b'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_bool_to_string(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 3], ElementTypeName.STRING)
    expect_column = pd.Series([None, 'True', 'False'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_category_to_string(data_frame):
    input_column = data_frame.iloc[:, 4]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series([np.nan, 'c', 'f'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_datetime_to_string():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series(['2019-01-29'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_timespan_to_string():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.STRING)
    expect_column = pd.Series(['5 days 00:00:00.000000000'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


def test_convert_column_by_element_type_nan_to_string():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.BOOL
"""


def test_convert_column_by_element_type_int_to_bool(data_frame):
    input_column = pd.Series([np.nan, 1, 2])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.BOOL)
    expect_column = pd.Series([np.nan, True, True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_float_to_bool(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.BOOL)
    expect_column = pd.Series([np.nan, True, True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_string_to_bool(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 2], ElementTypeName.BOOL)
    expect_column = pd.Series([np.nan, True, True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_bool_to_bool(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 3], ElementTypeName.BOOL)
    expect_column = data_frame.iloc[:, 3]
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_category_to_bool(data_frame):
    input_column = data_frame.iloc[:, 4]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.BOOL)
    expect_column = pd.Series([np.nan, True, True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_datetime_to_bool():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.BOOL)
    expect_column = pd.Series([True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_timespan_to_bool():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.BOOL)
    expect_column = pd.Series([True])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.BOOL


def test_convert_column_by_element_type_nan_to_bool():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.CATEGORY
"""


def test_convert_column_by_element_type_int_to_category(data_frame):
    input_column = pd.Series([np.nan, 1, 2])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = pd.Series([np.nan, 1.0, 2.0], dtype='category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_float_to_category(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = pd.Series([np.nan, 1.6, 1.0], dtype='category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_string_to_category(data_frame):
    compute_column = convert_column_by_element_type(data_frame.iloc[:, 2], ElementTypeName.CATEGORY)
    expect_column = pd.Series([np.nan, 'a', 'b'], dtype='category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_bool_to_category(data_frame):
    input_column = data_frame.iloc[:, 3]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = pd.Series([np.nan, 1.0, 0.0], dtype='category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_category_to_category(data_frame):
    input_column = data_frame.iloc[:, 4]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = pd.Series([np.nan, 'c', 'f'], dtype='category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_datetime_to_category():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = input_column.astype('category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_timespan_to_category():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.CATEGORY)
    expect_column = input_column.astype('category')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.CATEGORY


def test_convert_column_by_element_type_nan_to_category():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test [INT, FLOAT, STRING, BOOL, DATETIME, TIMESPAN, NAN] to CATEGORY and back to UNCATEGORY
"""


def test_original_type_to_category_back_to_uncategory(data_frame):
    for column_index in range(data_frame.shape[1]):

        # input column cannot be category, datetime or timespan type
        if column_index == 4 or column_index == 5 or column_index == 6:
            continue

        input_column = data_frame.iloc[:, column_index]
        category_column = input_column.astype('category')
        uncategory_column = convert_column_by_element_type(category_column, ElementTypeName.UNCATEGORY)
        assert uncategory_column.equals(input_column)


"""
Test function convert_column_by_element_type, target type is ElementTypeName.DATETIME
"""


def test_convert_column_by_element_type_int_to_datetime(data_frame):
    input_column = pd.Series([np.nan, 1, 2])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.DATETIME)
    expect_column = convert_to_datetime(pd.Series([np.nan, 1.0, 2.0]), unit='s')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.DATETIME


def test_convert_column_by_element_type_float_to_datetime(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.DATETIME)
    expect_column = convert_to_datetime(pd.Series([np.nan, 1.6, 1.0]), unit='s')
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.DATETIME


def test_convert_column_by_element_type_string_to_datetime(data_frame):
    input_column = pd.Series([np.nan, '20190101', '20190103'])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.DATETIME)
    expect_column = convert_to_datetime(input_column)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.DATETIME


def test_convert_column_by_element_type_bool_to_datetime(data_frame):
    input_column = data_frame.iloc[:, 3]
    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.DATETIME}":'):
        convert_column_by_element_type(input_column, ElementTypeName.DATETIME)


def test_convert_column_by_element_type_category_to_datetime(data_frame):
    input_column = pd.Series([np.nan, '20190101', '20190103'], dtype='category')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.DATETIME)
    expect_column = convert_to_datetime(input_column)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.DATETIME


def test_convert_column_by_element_type_datetime_to_datetime():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.DATETIME)
    expect_column = input_column
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.DATETIME


def test_convert_column_by_element_type_timespan_to_datetime():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.DATETIME}":'):
        convert_column_by_element_type(input_column, ElementTypeName.DATETIME)


def test_convert_column_by_element_type_nan_to_datetime():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.TIMESPAN
"""


def test_convert_column_by_element_type_int_to_timespan(data_frame):
    input_column = pd.Series([np.nan, 1, 2])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)
    expect_column = convert_to_time_span(pd.Series([np.nan, 1.0, 2.0]))
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.TIMESPAN


def test_convert_column_by_element_type_float_to_timespan(data_frame):
    input_column = data_frame.iloc[:, 1]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)
    expect_column = convert_to_time_span(pd.Series([np.nan, 1.6, 1.0]))
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.TIMESPAN


def test_convert_column_by_element_type_string_to_timespan(data_frame):
    input_column = pd.Series([np.nan, '20190101', '20190103'])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)
    expect_column = convert_to_time_span(input_column)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.TIMESPAN


def test_convert_column_by_element_type_bool_to_timespan(data_frame):
    input_column = data_frame.iloc[:, 3]
    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.TIMESPAN}":'):
        convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)


def test_convert_column_by_element_type_category_to_timespan(data_frame):
    input_column = pd.Series([np.nan, '20190101', '20190103'], dtype='category')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)
    expect_column = convert_to_time_span(input_column)
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.TIMESPAN


def test_convert_column_by_element_type_timespan_to_timespan():
    input_column = convert_to_time_span(pd.Series([5]), unit='days')
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)
    expect_column = input_column
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.TIMESPAN


def test_convert_column_by_element_type_datetime_to_timespan():
    input_column = convert_to_datetime(pd.Series(['20190129']), date_time_format='%Y%m%d')
    with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.TIMESPAN}":'):
        convert_column_by_element_type(input_column, ElementTypeName.TIMESPAN)


def test_convert_column_by_element_type_nan_to_timespan():
    input_column = pd.Series([np.nan, None, np.nan])
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.INT)
    assert input_column is compute_column


"""
Test function convert_column_by_element_type, target type is ElementTypeName.UNCATEGORY
"""


def test_convert_column_by_element_type_category_to_uncategory(data_frame):
    input_column = data_frame.iloc[:, 4]
    compute_column = convert_column_by_element_type(input_column, ElementTypeName.UNCATEGORY)
    expect_column = pd.Series([np.nan, 'c', 'f'])
    assert compute_column.equals(expect_column)
    assert DataFrameSchema.get_column_element_type(compute_column)[0] == ElementTypeName.STRING


"""
Test function convert_column_by_element_type, target type is ElementTypeName.NAN
"""


def test_convert_column_by_element_type_to_nan(data_frame):
    for column_index in range(data_frame.shape[1]):
        input_column = data_frame.iloc[:, column_index]
        with pytest.raises(TypeError, match=f'Cannot convert to type "{ElementTypeName.NAN}":'):
            convert_column_by_element_type(input_column, ElementTypeName.NAN)


@pytest.mark.parametrize(
    'string, target_type, expect_value',
    [
        ('1', ElementTypeName.INT, 1),
        ('1', ElementTypeName.FLOAT, 1.0),
        ('1', ElementTypeName.STRING, '1'),
        ('1', ElementTypeName.BOOL, True),
        ('0', ElementTypeName.BOOL, False),
        ('0.0', ElementTypeName.BOOL, False),
        ('true', ElementTypeName.BOOL, True),
        ('True', ElementTypeName.BOOL, True),
        ('TRUE', ElementTypeName.BOOL, True),
        ('false', ElementTypeName.BOOL, False),
        ('FALSE', ElementTypeName.BOOL, False),
        ('False', ElementTypeName.BOOL, False),
        ('2019/01/01', ElementTypeName.DATETIME, pd.Timestamp(2019, 1, 1)),
        ('1 day', ElementTypeName.TIMESPAN, pd.Timedelta('1 days 00:00:00')),
        ('3', ElementTypeName.CATEGORY, '3'),
        ('3', ElementTypeName.NAN, '3')
    ]
)
def test_convert_string_by_element_type(string, target_type, expect_value):
    compute_value = convert_scalar_by_element_type(string, target_type)
    assert compute_value == expect_value


@pytest.mark.parametrize(
    'invalid_string',
    ['yes', 'no', 'YES', 'NO', '1.1.1', '0.0.1']
)
def test_convert_string_bool_error(invalid_string):
    with pytest.raises(RuntimeError, match='Cannot convert to type "bool": Not a valid boolean value:'):
        convert_scalar_by_element_type(invalid_string, ElementTypeName.BOOL)


def test_drop_na_and_convert_duplicated_index():
    series = pd.Series([1, 2, np.nan, np.nan], index=[1, 1, 2, 2])
    new_series = _drop_na_and_convert(series, 'str')
    expected_series = pd.Series(['1.0', '2.0', np.nan, np.nan], index=[1, 1, 2, 2])
    assert new_series.equals(expected_series)

import pytest
import copy

import pandas as pd
import numpy as np

from azureml.studio.common.datatable.data_table import DataTableColumnSelection, DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.io.data_table_io import write_data_table, read_data_table
from azureml.studio.core.io.data_frame_visualizer import DataFrameVisualizer
from azureml.studio.common.utils.datetimeutils import convert_to_datetime
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.modulehost.constants import ElementTypeName, ColumnTypeName
from azureml.studio.modules.datatransform.manipulation.metadata_editor.metadata_editor \
    import MetadataEditorDataType, MetadataEditorCategorical, \
    MetadataEditorFlag, MetadataEditorModule
from azureml.studio.common.error import ModuleError, ParameterParsingError, ErrorConvertingColumnError, \
    CouldNotConvertColumnError, MultipleLabelColumnsError


def create_data_frame():
    data_frame = pd.DataFrame()
    data_frame['col0'] = [2, 1, 10]
    data_frame['col1'] = [np.nan, 1.6, 1]
    data_frame['col2'] = [np.nan, 'a', 'b']
    data_frame['col3'] = [None, True, False]
    data_frame['col4'] = pd.Series([np.nan, 'c', 'f']).astype(ElementTypeName.CATEGORY)
    data_frame['col5'] = ['20190201', '20190129', '20131011']
    data_frame['col6'] = [90, 30, 80]
    return data_frame


def create_data_table():
    return DataTable(create_data_frame())


DATE_TIME_FORMAT = '%Y%m%d'
TIME_SPAN_FORMAT = 'D'
TO_DATE_TIME_ERRORS = 'coerce'
TO_TIME_SPAN_ERRORS = 'coerce'


def column_selection_col01():
    return DataTableColumnSelection(
        '{"isFilter":true,"rules":['
        '{"ruleType":"ColumnNames","columns":'
        '["col0","col1"],"exclude":false}]}')


@pytest.mark.parametrize(
    "col_indexes, new_data_type, expected_type", [
        ([0, 1], MetadataEditorDataType.String, ElementTypeName.STRING),
        ([1], MetadataEditorDataType.Integer, ElementTypeName.INT),
        ([0], MetadataEditorDataType.Double, ElementTypeName.FLOAT),
        ([5], MetadataEditorDataType.DateTime, ElementTypeName.DATETIME),
        ([6], MetadataEditorDataType.TimeSpan, ElementTypeName.TIMESPAN)
    ])
def test_change_column_element_type(
        col_indexes, new_data_type, expected_type):

    dt = create_data_table()
    df = create_data_frame()

    MetadataEditorModule.change_columns_element_type(
        dt, col_indexes, new_data_type,
        DATE_TIME_FORMAT, TIME_SPAN_FORMAT
    )

    for col_index in col_indexes:
        if expected_type == ElementTypeName.DATETIME:
            assert dt.get_column(col_index).equals(
                pd.to_datetime(arg=df.iloc[:, col_index],
                               format=DATE_TIME_FORMAT, errors=TO_DATE_TIME_ERRORS))
        elif expected_type == ElementTypeName.TIMESPAN:
            assert dt.get_column(col_index).equals(
                pd.to_timedelta(arg=df.iloc[:, col_index],
                                unit=TIME_SPAN_FORMAT, errors=TO_TIME_SPAN_ERRORS))
        else:
            df.iloc[:, col_index] = df.iloc[:, col_index].dropna().astype(expected_type)
            assert dt.get_column(col_index).equals(
                df.iloc[:, col_index])


def test_could_not_convert_column_error_change_column_element_type():
    dt = create_data_table()
    col_indexes = [2]
    new_data_type = MetadataEditorDataType.Integer

    with pytest.raises(CouldNotConvertColumnError,
                       match='Could not convert column of type String to column of type int64.'):
        MetadataEditorModule.change_columns_element_type(
            dt, col_indexes, new_data_type,
            DATE_TIME_FORMAT, TIME_SPAN_FORMAT
        )


def test_parameter_parsing_error_change_column_element_type():
    dt = create_data_table()
    col_indexes = [0, 1]
    new_data_type = 'apple'
    with pytest.raises(ParameterParsingError):
        MetadataEditorModule.change_columns_element_type(
            dt, col_indexes, new_data_type,
            DATE_TIME_FORMAT, TIME_SPAN_FORMAT
        )


@pytest.mark.parametrize(
    "col_indexes, new_categorical, expected_type", [
        ([0, 1], MetadataEditorCategorical.Unchanged, 'unchanged'),
        ([0, 2], MetadataEditorCategorical.Categorical, ElementTypeName.CATEGORY),
        ([0, 1], MetadataEditorCategorical.NonCategorical, ElementTypeName.UNCATEGORY),
    ])
def test_change_categorical_column(col_indexes, new_categorical, expected_type):

    dt = create_data_table()
    df = create_data_frame()

    if (expected_type == 'unchanged') or (expected_type == ElementTypeName.CATEGORY):
        MetadataEditorModule.change_categorical_columns(
            dt, col_indexes, new_categorical)
        if expected_type == 'unchanged':
            for col_index in col_indexes:
                assert dt.get_column(col_index).equals(
                    df.iloc[:, col_index])
        else:
            for col_index in col_indexes:
                assert dt.get_column(col_index).equals(
                    df.iloc[:, col_index].astype(expected_type))
                assert dt.get_column_type(col_index) == ColumnTypeName.CATEGORICAL
                assert dt.get_element_type(col_index) == ElementTypeName.CATEGORY
    else:
        MetadataEditorModule.change_categorical_columns(
            dt, col_indexes, MetadataEditorCategorical.Categorical)

        MetadataEditorModule.change_categorical_columns(
            dt, col_indexes, MetadataEditorCategorical.NonCategorical)

        for col_index in col_indexes:
            assert dt.get_column(col_index).equals(
                df.iloc[:, col_index])


def test_astype_category():
    df = create_data_frame()
    for col_name in list(df.columns):
        column_new = df[col_name].dropna()
        for row_index in column_new.index:
            assert column_new.astype(ElementTypeName.CATEGORY)[row_index] == \
                   column_new[row_index]


def test_parameter_parsing_error_change_categorical_column():

    with pytest.raises(ParameterParsingError):
        dt = create_data_table()
        col_indexes = [0, 1]
        new_categorical = 'apple'
        MetadataEditorModule.change_categorical_columns(
            dt, col_indexes, new_categorical)


def test_convert_column_error_change_categorical_column():
    dt = DataTable()
    col_indexes = [1]
    with pytest.raises(ErrorConvertingColumnError, match='Failed to convert column to Categorical.'):
        MetadataEditorModule.change_categorical_columns(
            dt, col_indexes, MetadataEditorCategorical.Categorical
        )


@pytest.mark.parametrize(
    'col_indexes, new_field', [
        ([0, 1], MetadataEditorFlag.Unchanged),
        ([0], MetadataEditorFlag.Features),
        ([3], MetadataEditorFlag.Labels),
        ([3, 4], MetadataEditorFlag.ClearFeatures),
        ([5], MetadataEditorFlag.ClearLabels),
        ([4, 5], MetadataEditorFlag.ClearScores)
    ])
def test_change_feature_label_columns(col_indexes, new_field):
    dt = create_data_table()
    if new_field == MetadataEditorFlag.Unchanged:
        dt_new = copy.deepcopy(dt)
        MetadataEditorModule.change_feature_label_columns(dt_new, col_indexes, new_field)
        for col_index in col_indexes:
            assert dt.meta_data.column_attributes[col_index] == \
                   dt_new.meta_data.column_attributes[col_index]

    elif new_field == MetadataEditorFlag.Labels:
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)
        for col_index in col_indexes:
            assert dt.meta_data.label_column_name == dt.column_names[col_index]

    elif new_field == MetadataEditorFlag.Features:
        MetadataEditorModule.change_feature_label_columns(
            dt, col_indexes, MetadataEditorFlag.Labels)
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)
        for col_index in col_indexes:
            assert dt.meta_data.column_attributes[col_index].is_feature

    elif new_field == MetadataEditorFlag.ClearFeatures:
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)
        for col_index in col_indexes:
            assert not dt.meta_data.column_attributes[col_index].is_feature

    elif new_field == MetadataEditorFlag.ClearLabels:
        MetadataEditorModule.change_feature_label_columns(
            dt, col_indexes, MetadataEditorFlag.Labels)
        for col_index in col_indexes:
            assert dt.meta_data.label_column_name == dt.column_names[col_index]
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)
        assert not dt.meta_data.label_column_name

    elif new_field == MetadataEditorFlag.ClearScores:
        dt.meta_data.score_column_names = {'score_type1': 'col1'}
        dt.meta_data.score_column_names = {'score_type2': 'col2'}
        assert dt.meta_data.score_column_names == {'score_type1': 'col1', 'score_type2': 'col2'}
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)
        assert not dt.meta_data.score_column_names


def test_error_change_feature_label_columns():
    dt = create_data_table()
    col_indexes = [0, 1]

    with pytest.raises(MultipleLabelColumnsError, match='Multiple label columns are specified.'):
        new_field = MetadataEditorFlag.Labels
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)

    with pytest.raises(ParameterParsingError):
        new_field = 'apple'
        MetadataEditorModule.change_feature_label_columns(dt, col_indexes, new_field)


def test_change_column_name():
    dt = create_data_table()
    col_indexes = [0, 1, 3, 5]
    new_col_names = 'col_0,col_1,col_3,col_5'
    MetadataEditorModule.change_column_names(dt, col_indexes, new_col_names)
    assert dt.column_names == ['col_0', 'col_1', 'col2', 'col_3', 'col4', 'col_5', 'col6']
    assert dt.meta_data.column_attributes[0].name == 'col_0'


def test_error_change_column_name():
    dt = create_data_table()
    col_indexes = [0, 1, 3, 5]
    with pytest.raises(
            ModuleError,
            match='The size of "New column names" is inconsistent with size of "Column".'):
        new_col_names = 'col_0,col_1,col_3'
        MetadataEditorModule.change_column_names(dt, col_indexes, new_col_names)

    with pytest.raises(
            ModuleError,
            match='The name "col_3" is duplicated in "New column names".'):
        new_col_names = 'col_0,col_1,col_3,col_3'
        MetadataEditorModule.change_column_names(dt, col_indexes, new_col_names)

    with pytest.raises(
            ModuleError,
            match='The name "col5" is duplicated in "column names in input dataset".'):
        col_indexes = [0, 1, 3]
        new_col_names = 'col_0,col_1,col5'
        MetadataEditorModule.change_column_names(dt, col_indexes, new_col_names)


def test_run():
    dt = create_data_table()
    df = create_data_frame()
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["col0"],"exclude":false}]}')
    new_data_type = MetadataEditorDataType.Unchanged
    new_categorical = MetadataEditorCategorical.Categorical
    new_field = MetadataEditorFlag.Labels
    new_col_name = 'col_0'

    # pylint: disable=no-value-for-parameter
    result_table = MetadataEditorModule.run(
        table=dt,
        column_select=col_select,
        new_data_type=new_data_type,
        new_categorical=new_categorical,
        new_field=new_field,
        new_column_names=new_col_name,
        date_time_format=DATE_TIME_FORMAT,
        time_span_format=TIME_SPAN_FORMAT)[0]

    assert result_table.get_column(0).equals(df.iloc[:, 0].astype(ElementTypeName.CATEGORY))
    assert result_table.meta_data.label_column_name == new_col_name
    assert result_table.column_names[0] == new_col_name


@pytest.mark.parametrize(
    'dt, col_select, match', [
        (None, column_selection_col01(), 'Input "Dataset" is null or empty'),
        (create_data_table(), None, 'Input "Column" is null or empty')
    ])
def test_run_error_null_or_empty(dt, col_select, match):
    with pytest.raises(ModuleError, match=match):
        # pylint: disable=no-value-for-parameter
        MetadataEditorModule.run(
            table=dt,
            column_select=col_select)


def test_run_error_too_few_columns_in_dataset():
    df = pd.DataFrame()
    dt = DataTable(df)

    with pytest.raises(
            ModuleError,
            match='Number of columns in input dataset "Dataset" is less than allowed minimum of 1 column'):
        col_select = DataTableColumnSelection(
            '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["col0"],"exclude":false}]}')
        # pylint: disable=no-value-for-parameter
        MetadataEditorModule.run(
            table=dt,
            column_select=col_select,
            new_data_type=MetadataEditorDataType.Unchanged,
            new_categorical=MetadataEditorCategorical.Unchanged,
            new_field=MetadataEditorFlag.Unchanged
        )


"""
Convert date type, compute visualization file and write the output data table to parquet
compute visualization file is simply a smoke test
"""


def write_to_parquet_and_read_back_to_validate(tmpdir, dt: DataTable):
    temp_file = generate_random_string()
    dataset_file_name = str(tmpdir.join(f"{temp_file}.dataset.parquet"))
    write_data_table(dt, dataset_file_name)
    output_data_table = read_data_table(dataset_file_name)
    assert output_data_table.data_frame.equals(dt.data_frame)
    assert output_data_table.meta_data.column_attributes == dt.meta_data.column_attributes


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['apple', None]}), pd.DataFrame({'col0': ['apple', None]})),  # string
        (pd.DataFrame({'col0': [1, np.nan]}), pd.DataFrame({'col0': ['1.0', np.nan]})),  # int/float
        (pd.DataFrame({'col0': [True, np.nan]}), pd.DataFrame({'col0': ['True', np.nan]})),  # Bool
        (pd.DataFrame({'col0': [1, np.nan]}).astype('category'), pd.DataFrame({'col0': ['1.0', np.nan]})),  # category
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190101', np.nan]))}),
            pd.DataFrame({'col0': ['2019-01-01', np.nan]})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_string_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.String,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['1', None]}), pd.DataFrame({'col0': [1.0, np.nan]})),  # string
        (pd.DataFrame({'col0': [1, np.nan]}), pd.DataFrame({'col0': [1, np.nan]})),  # int/float
        (pd.DataFrame({'col0': [True, np.nan]}), pd.DataFrame({'col0': [1, np.nan]})),  # bool
        (pd.DataFrame({'col0': [1, np.nan]}).astype('category'), pd.DataFrame({'col0': [1, np.nan]})),  # category
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))}),
            pd.DataFrame({'col0': [1548720000, np.nan]})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_integer_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Integer,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['1', None]}), pd.DataFrame({'col0': [1.0, np.nan]})),  # string
        (pd.DataFrame({'col0': [1, np.nan]}), pd.DataFrame({'col0': [1, np.nan]})),  # int/float
        (pd.DataFrame({'col0': [True, np.nan]}), pd.DataFrame({'col0': [1, np.nan]})),  # bool
        (pd.DataFrame({'col0': [1, np.nan]}).astype('category'), pd.DataFrame({'col0': [1, np.nan]})),  # category
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))}),
            pd.DataFrame({'col0': [1548720000, np.nan]})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_double_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Double,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['1', None]}), pd.DataFrame({'col0': [True, None]})),  # string
        (pd.DataFrame({'col0': [1, np.nan]}), pd.DataFrame({'col0': [True, np.nan]})),  # int/float
        (pd.DataFrame({'col0': [True, np.nan]}), pd.DataFrame({'col0': [True, np.nan]})),  # bool
        (pd.DataFrame({'col0': [1, np.nan]}).astype('category'), pd.DataFrame({'col0': [True, np.nan]})),  # category
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))}),
            pd.DataFrame({'col0': [True, np.nan]})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_bool_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Boolean,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['20070501', np.nan]}),
            pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20070501', np.nan]))})),  # string
        (pd.DataFrame({'col0': [20190129, np.nan]}),
            pd.DataFrame({'col0': convert_to_datetime(pd.Series([20190129, np.nan]), unit='s')})),  # int/float
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))}),
            pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_datetime_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.DateTime,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        # string
        (
                pd.DataFrame({'col0': ['1', None]}),
                pd.DataFrame({'col0': ['1', None]}).astype('category')
        ),
        # int/float
        (
                pd.DataFrame({'col0': [1, np.nan]}),
                pd.DataFrame({'col0': [1, np.nan]}).astype('category')
        ),
        # bool BUG id:411099 fixed
        (
                pd.DataFrame({'col0': [True, np.nan]}),
                pd.DataFrame({'col0': [1, np.nan]}).astype('category')
        ),
        # category
        (
                pd.DataFrame({'col0': [1, np.nan]}).astype('category'),
                pd.DataFrame({'col0': [1, np.nan]}).astype('category')
        ),
        # Datetime BUG id:411113 fixed
        (
                pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', '20190101']))}),
                pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', '20190101']))}).astype('category')
        ),
        # nan
        (
                pd.DataFrame({'col0': [np.nan, None]}),
                pd.DataFrame({'col0': [np.nan, None]})
        )
    ]
)
def test_convert_to_category_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Unchanged,
        new_categorical=MetadataEditorCategorical.Categorical,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


@pytest.mark.parametrize(
    'input_df, expect_df',
    [
        (pd.DataFrame({'col0': ['1', None]}).astype('category'), pd.DataFrame({'col0': ['1', None]})),  # string
        (pd.DataFrame({'col0': [1, np.nan]}).astype('category'), pd.DataFrame({'col0': [1, np.nan]})),  # int/float
        (pd.DataFrame({'col0': [True, np.nan]}).astype('category'), pd.DataFrame({'col0': [True, np.nan]})),  # bool
        (pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))}).astype('category'),
            pd.DataFrame({'col0': convert_to_datetime(pd.Series(['20190129', np.nan]))})),  # Datetime
        (pd.DataFrame({'col0': [np.nan, None]}), pd.DataFrame({'col0': [np.nan, None]}))  # nan
    ]
)
def test_convert_to_noncategory_visualize_and_write_parquet(tmpdir, input_df, expect_df):
    dt = DataTable(input_df)
    compute_dt = MetadataEditorModule.run(
        table=dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Unchanged,
        new_categorical=MetadataEditorCategorical.NonCategorical,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]
    assert compute_dt.data_frame.equals(expect_df)
    # Smoke test of generating visualization file
    DataFrameVisualizer(compute_dt.data_frame, schema=compute_dt.meta_data)
    # Dump to parquet and read back
    write_to_parquet_and_read_back_to_validate(tmpdir, compute_dt)


def test_bool_column_to_category_can_be_recovered():
    # Input bool column
    input_df = pd.DataFrame({'col0': [True, np.nan]})
    input_dt = DataTable(input_df)

    # Convert to category
    category_dt = MetadataEditorModule.run(
        table=input_dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Unchanged,
        new_categorical=MetadataEditorCategorical.Categorical,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]

    # Convert to int
    int_dt = MetadataEditorModule.run(
        table=category_dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Unchanged,
        new_categorical=MetadataEditorCategorical.NonCategorical,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]

    # Convert to bool
    bool_dt = MetadataEditorModule.run(
        table=int_dt,
        column_select=DataTableColumnSelectionBuilder().include_col_names('col0').build(),
        new_data_type=MetadataEditorDataType.Boolean,
        new_categorical=MetadataEditorCategorical.Unchanged,
        new_field=MetadataEditorFlag.Unchanged,
        new_column_names=None,
        date_time_format=None,
        time_span_format=None
    )[0]

    # Validate the recovered bool column is the same as the input bool column
    assert input_dt.data_frame.equals(bool_dt.data_frame)
    assert input_dt.meta_data.column_attributes == bool_dt.meta_data.column_attributes

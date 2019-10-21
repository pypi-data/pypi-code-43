import os

import pytest
import pandas as pd
import numpy as np

from azureml.studio.common.error import ColumnNotFoundError, InvalidColumnTypeError, ParameterParsingError
from azureml.studio.common.io.data_table_io import read_data_table
from azureml.studio.core.io.data_frame_visualizer import DataFrameVisualizer
from azureml.studio.modules.dataio.import_data.web_reader import WebSourceDataFormat
from azureml.studio.modules.datatransform.clean_missing_data.clean_missing_transform \
    import CleanMissingValueTransform, CleanMissingDataHandlingPolicy
from azureml.studio.modules.datatransform.clean_missing_data.clean_missing_data \
    import CleanMissingDataModule, ColumnsWithAllValuesMissing
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.modules.dataio.import_data.import_data import \
    ImportDataModule, ReaderDataSourceOrSink


@pytest.fixture
def data_frame():
    df = pd.DataFrame()
    df['col0'] = [2, 1, 10]
    df['col1'] = [np.nan, 1.6, 1]
    df['col2'] = [np.nan, 'a', 'b']
    df['col3'] = [None, True, False]
    df['col4'] = [None, np.nan, None]
    return df


@pytest.fixture
def empty_data_frame(data_frame):
    return data_frame.drop([0, 1, 2]).reset_index(drop=True)


@pytest.fixture
def data_table(data_frame):
    return DataTable(data_frame)


def validate_meta_data(compute_meta_data, expect_meta_data):
    assert compute_meta_data.column_attributes == expect_meta_data.column_attributes
    assert compute_meta_data.score_column_names == expect_meta_data.score_column_names
    assert compute_meta_data.label_column_name == expect_meta_data.label_column_name
    assert compute_meta_data.feature_channels == expect_meta_data.feature_channels


def validate_data_table(compute_dt, expect_dt):
    # Validate data frame
    assert compute_dt.data_frame.equals(expect_dt.data_frame)
    validate_meta_data(compute_dt.meta_data, expect_dt.meta_data)


def test_get_column_indexes_with_wanted_ratio(data_table):
    compute_column_indexes = CleanMissingValueTransform.get_column_indexes_with_wanted_ratio(
        dt=data_table,
        col_indexes=[1, 2, 3, 4],
        min_ratio=0.2,
        max_ratio=0.9
    )
    expect_column_indexes = [1, 2, 3]
    assert compute_column_indexes == expect_column_indexes


def test_replace_with_mean_remove_columns_with_all_missing_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mean(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mean_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mean(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]
    expect_df['col4_IsMissing'] = [True, True, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mean_remove_columns_with_all_missing(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mean(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mean(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mean(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])
    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]
    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_median_remove_columns_with_all_missing_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_median(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_median_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_median(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]
    expect_df['col4_IsMissing'] = [True, True, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_median_remove_columns_with_all_missing(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_median(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_median(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_median(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mode_remove_columns_with_all_missing_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mode(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 2, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = ['a', 'a', 'b']
    expect_df['col3'] = [True, True, False]

    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col2_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mode_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mode(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]

    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]
    expect_df['col4_IsMissing'] = [True, True, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mode_remove_columns_with_all_missing(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mode(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mode(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_mode(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.3, 1.6, 1]
    expect_df['col2'] = [np.nan, 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = [None, np.nan, None]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_value_remove_columns_with_all_missing_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_value(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 2, 3, 4],
        replacement_value='0')

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [0, 1.6, 1]
    expect_df['col2'] = ['0', 'a', 'b']
    expect_df['col3'] = [False, True, False]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col2_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_value_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_value(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 2, 3, 4],
        replacement_value='1.5')

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [1.5, 1.6, 1]
    expect_df['col2'] = ['1.5', 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = ['1.5', '1.5', '1.5']
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col2_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]
    expect_df['col4_IsMissing'] = [True, True, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_value_remove_columns_with_all_missing(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_value(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 2, 3, 4],
        replacement_value='-1.5')

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [-1.5, 1.6, 1]
    expect_df['col2'] = ['-1.5', 'a', 'b']
    expect_df['col3'] = [True, True, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_value(data_table):
    compute_dt = CleanMissingValueTransform.replace_with_value(
        data_table,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0, 1, 2, 3, 4],
        replacement_value='-1.5')

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [-1.5, 1.6, 1]
    expect_df['col2'] = ['-1.5', 'a', 'b']
    expect_df['col3'] = [True, True, False]
    expect_df['col4'] = ['-1.5', '-1.5', '-1.5']

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_value_data_time():
    """
    BUG 402326
    """
    df = pd.DataFrame()
    df['col0'] = pd.to_datetime(
        arg=pd.Series([np.nan, '20190129', np.nan]), format='%Y%m%d', errors='coerce')
    input_dt = DataTable(df)
    compute_dt = CleanMissingValueTransform.replace_with_value(
        input_dt,
        remove_columns_with_all_missing=False,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[0],
        replacement_value='20190403')
    expect_df = pd.DataFrame()
    expect_df['col0'] = pd.to_datetime(
        arg=pd.Series(['20190403', '20190129', '20190403']), format='%Y%m%d', errors='coerce')
    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_check_column_types_for_numeric_transforms_error_message(data_table):
    expect_error_message = \
        'Cannot process column "col2" of type str. The type is not supported by the module. Parameter name: Dataset'

    with pytest.raises(InvalidColumnTypeError, match=expect_error_message):
        CleanMissingValueTransform.replace_with_mean(
            data_table,
            remove_columns_with_all_missing=True,
            generate_missing_value_indicator_columns=True,
            columns_to_clean_indexes=[2])


@pytest.mark.parametrize(
    'col_idx, to_type, value',
    [
        (1, 'float64', 'apple'),
        (3, 'bool', 'apple'),
    ]
)
def test_convert_replacement_value_error_message(data_table, col_idx, to_type, value):
    expect_error_message_tpl = \
        """Failed to convert "col{col_idx}" parameter value "{value}" from "str" to "{to_type}"""
    expect_error_message = expect_error_message_tpl.format(col_idx=col_idx, to_type=to_type, value=value)
    with pytest.raises(ParameterParsingError, match=expect_error_message):
        CleanMissingValueTransform.replace_with_value(
            data_table,
            remove_columns_with_all_missing=True,
            generate_missing_value_indicator_columns=True,
            columns_to_clean_indexes=[col_idx],
            replacement_value=value)


def test_remove_column_generate_missing_value_indicator_columns(data_table):
    compute_dt = CleanMissingValueTransform.remove_column(
        data_table,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0, 1, 2])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]

    expect_df['col3'] = [None, True, False]
    expect_df['col4'] = [None, np.nan, None]
    expect_df['col0_IsMissing'] = [False, False, False]

    expect_dt = DataTable(expect_df)

    validate_data_table(expect_dt, compute_dt)


def test_remove_column(data_table):
    compute_dt = CleanMissingValueTransform.remove_column(
        data_table,
        generate_missing_value_indicator_columns=False,
        columns_to_clean_indexes=[1, 2])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col3'] = [None, True, False]
    expect_df['col4'] = [None, np.nan, None]
    expect_dt = DataTable(expect_df)

    validate_data_table(expect_dt, compute_dt)


def test_remove_row_remove_columns_with_all_missing(data_table):
    compute_dt = CleanMissingValueTransform.remove_row(
        data_table,
        remove_columns_with_all_missing=True,
        columns_to_clean_indexes=[0, 1, 2, 3, 4])

    expect_df = pd.DataFrame()
    expect_df['col0'] = [1, 10]
    expect_df['col1'] = [1.6, 1]
    expect_df['col2'] = ['a', 'b']
    expect_df['col3'] = pd.Series([True, False]).astype('object')
    expect_dt = DataTable(expect_df)

    validate_data_table(expect_dt, compute_dt)


def test_remove_row(data_table, empty_data_frame):
    compute_dt = CleanMissingValueTransform.remove_row(
        data_table,
        remove_columns_with_all_missing=False,
        columns_to_clean_indexes=[1])
    expect_df = pd.DataFrame()
    expect_df['col0'] = [1, 10]
    expect_df['col1'] = [1.6, 1]
    expect_df['col2'] = ['a', 'b']
    expect_df['col3'] = pd.Series([True, False]).astype('object')
    expect_df['col4'] = [np.nan, None]
    expect_dt = DataTable(expect_df)

    validate_data_table(expect_dt, compute_dt)


def test_apply(data_table):
    clean_mv_transform = CleanMissingValueTransform(
        cleaning_mode=CleanMissingDataHandlingPolicy.ReplaceWithValue,
        replacement_value='0',
        remove_columns_with_all_missing=True,
        indicator_columns=True,
        column_names=data_table.column_names,
        min_ratio=0,
        max_ratio=1)

    compute_dt = clean_mv_transform.apply(data_table)

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [0, 1.6, 1]
    expect_df['col2'] = ['0', 'a', 'b']
    expect_df['col3'] = [False, True, False]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col2_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_apply_column_not_found_error(data_table):
    clean_mv_transform = CleanMissingValueTransform(
        cleaning_mode=CleanMissingDataHandlingPolicy.ReplaceWithValue,
        replacement_value='0',
        remove_columns_with_all_missing=True,
        indicator_columns=True,
        column_names=['col1000'],
        min_ratio=0,
        max_ratio=1)
    with pytest.raises(
            ColumnNotFoundError,
            match='Column with name or index "col1000" does not exist in "Dataset", but exists in "Transformation"'):
        clean_mv_transform.apply(data_table)


def test_run(data_table):

    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false}],"ui":{"withRules":true}}')
    # pylint: disable=no-value-for-parameter
    compute_dt, compute_transform = CleanMissingDataModule.run(
        input_data=data_table,
        columns_to_clean=column_selection,
        min_ratio=0.0,
        max_ratio=1.0,
        cleaning_mode=CleanMissingDataHandlingPolicy.ReplaceWithValue,
        replacement_value='0',
        cols_with_all_missing=ColumnsWithAllValuesMissing.Remove,
        generate_missing_value_indicator_column=True)

    expect_df = pd.DataFrame()
    expect_df['col0'] = [2, 1, 10]
    expect_df['col1'] = [0, 1.6, 1]
    expect_df['col2'] = ['0', 'a', 'b']
    expect_df['col3'] = [False, True, False]
    expect_df['col0_IsMissing'] = [False, False, False]
    expect_df['col1_IsMissing'] = [True, False, False]
    expect_df['col2_IsMissing'] = [True, False, False]
    expect_df['col3_IsMissing'] = [True, False, False]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)
    assert isinstance(compute_transform, CleanMissingValueTransform)


def test_custom_data_table():
    # pylint: disable=no-value-for-parameter
    output = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="http://samplecsvs.s3.amazonaws.com/TechCrunchcontinentalUSA.csv",
        csv_tsv_has_header=True,
        data_format=WebSourceDataFormat.CSV)

    dt = output[0]

    compute_dt = CleanMissingValueTransform.remove_row(
        dt,
        remove_columns_with_all_missing=False,
        columns_to_clean_indexes=[0])

    assert compute_dt


@pytest.mark.skip
def test_with_big_dataset():
    def script_directory():
        return os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_directory(), 'gen', 'data_2.dataset')
    dt = read_data_table(file_name)

    DataFrameVisualizer(dt.data_frame, schema=dt.meta_data.to_dict())

    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false}],"ui":{"withRules":true}}')
    # pylint: disable=no-value-for-parameter
    compute_dt, compute_transform = CleanMissingDataModule.run(
        input_data=dt,
        columns_to_clean=column_selection,
        min_ratio=0.0,
        max_ratio=1.0,
        cleaning_mode=CleanMissingDataHandlingPolicy.RemoveRow,
        replacement_value='0',
        cols_with_all_missing=ColumnsWithAllValuesMissing.Remove,
        generate_missing_value_indicator_column=True)


def test_error_validate_column_types_for_numeric_transforms(data_table):
    with pytest.raises(
            InvalidColumnTypeError,
            match='Cannot process column "col2" of type str. The type is not supported by the module. '
                  'Parameter name: Dataset'
    ):
        CleanMissingValueTransform.replace_with_mean(
            data_table,
            remove_columns_with_all_missing=False,
            generate_missing_value_indicator_columns=False,
            columns_to_clean_indexes=[2])


def test_generate_replacement_for_column_name_error():
    pass


# To fix bug 492697
def test_replace_with_value_of_categorical_column():
    data_table = DataTable(pd.DataFrame({'col0': pd.Series(['a', 'b', None], dtype='category')}))
    compute_dt = CleanMissingValueTransform.replace_with_value(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0],
        replacement_value='NA')

    expect_df = pd.DataFrame()
    expect_df['col0'] = pd.Series(['a', 'b', 'NA'], dtype='category')
    expect_df['col0_IsMissing'] = [False, False, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)


def test_replace_with_mode_of_categorical_column():
    data_table = DataTable(pd.DataFrame({'col0': pd.Series(['a', 'a', None], dtype='category')}))
    compute_dt = CleanMissingValueTransform.replace_with_mode(
        data_table,
        remove_columns_with_all_missing=True,
        generate_missing_value_indicator_columns=True,
        columns_to_clean_indexes=[0]
    )

    expect_df = pd.DataFrame()
    expect_df['col0'] = pd.Series(['a', 'a', 'a'], dtype='category')
    expect_df['col0_IsMissing'] = [False, False, True]

    expect_dt = DataTable(expect_df)
    validate_data_table(expect_dt, compute_dt)

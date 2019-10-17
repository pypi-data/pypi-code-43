import numpy as np
import pandas as pd
import pytest

import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_type_conversion import convert_column_by_element_type
from azureml.studio.core.data_frame_schema import ElementTypeName
from azureml.studio.core.utils.column_selection import ColumnKind
from azureml.studio.modules.datatransform.manipulation.smote.smote import SMOTEModule


@pytest.fixture
def dataset_smote():
    data = DataTable(pd.DataFrame(
        {
            'feature1': [32, 34, 34, 32, 21, 32],
            'feature2': [32, 43, 54, 32, 43, 54],
            'feature3': convert_column_by_element_type(
                pd.Series(['20111230', '20111130', '20111130', '20121230', '20121230', '20131230']),
                ElementTypeName.DATETIME),
            'class': [0, 0, 1, 0, 1, 0]
        }
    ))

    return data


@pytest.fixture(params=[str, 'category'])
def dataset_cate_label(request):
    data = pd.DataFrame(
        {
            'feature1': [32, 34, 34, 32, 21, 32],
            'feature2': [32, 43, 54, 32, 43, 54],
            'class': ['0', '0', '1', '0', '1', '0']
        })
    data_type = request.param
    data['class'] = data['class'].astype(data_type)
    return DataTable(data)


@pytest.fixture(params=[str, 'category'])
def dataset_smote_with_string(request):
    data = pd.DataFrame(
        {
            'feature1': ['asd', 'gfd', 'weq', 'fds', 'ewq', 'fds'],
            'feature2': [32, 43, 54, 32, 43, 54],
            'class': [0, 0, 1, 0, 1, 0]

        }
    )
    data['feature1'] = data['feature1'].astype(request.param)

    return DataTable(data)


@pytest.fixture
def dataset_table_null():
    data = DataTable(pd.DataFrame(
        {
            'feature1': [],
            'feature2': [],
            'class': []
        }
    ))

    return data


@pytest.fixture
def dataset_smote_with_multi_class():
    data = DataTable(pd.DataFrame(
        {
            'feature1': [32, 34, 34, 32, 21, 32],
            'feature2': [32, 43, 54, 32, 43, 54],
            'class': [0, 0, 1, 2, 1, 1]
        }
    ))

    return data


@pytest.fixture
def dataset_smote_with_no_feature_column():
    data = DataTable(pd.DataFrame(
        {
            'class': [0, 0, 1, 0, 1, 0]
        }
    ))

    return data


def test_run_cate_label(dataset_cate_label):
    # Test the correct datatable
    target_name = 'class'
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names(target_name).build()
    output_dt, = SMOTEModule._run_impl(
        samples=dataset_cate_label,
        label_column_index_or_name=column_selection,
        smote_percent=100,
        neighbors=1,
        seed=0)

    actual_minority_category_rows_num = 4
    label_to_num = pd.value_counts(output_dt.data_frame['class'])
    expected_minority_category_rows_num = min(label_to_num)

    assert actual_minority_category_rows_num == expected_minority_category_rows_num


def test_run_smote(dataset_smote):
    # Test the correct datatable

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    output_dt, = SMOTEModule._run_impl(
        samples=dataset_smote,
        label_column_index_or_name=column_selection,
        smote_percent=100,
        neighbors=1,
        seed=0)

    actual_minority_category_rows_num = 4
    label_to_num = pd.value_counts(output_dt.data_frame['class'])
    expected_minority_category_rows_num = min(label_to_num)

    assert actual_minority_category_rows_num == expected_minority_category_rows_num


def test_illegal_neighbors(dataset_smote):
    # Test the datatable with illegal neighbors parameter

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    with pytest.raises(error_setting.LessThanOrEqualToError):
        SMOTEModule._run_impl(
            samples=dataset_smote,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=2,
            seed=0)


def test_illegal_synthetic_ratio(dataset_smote):
    # Test the datatable with illegal syntheticRatio

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    with pytest.raises(error_setting.NotInRangeValueError):
        SMOTEModule._run_impl(
            samples=dataset_smote,
            label_column_index_or_name=column_selection,
            smote_percent=200,
            neighbors=1,
            seed=0)


def test_zero_smote_percent(dataset_smote):
    # Test the datatable with zero smote percent parameter

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    output_dt, = SMOTEModule._run_impl(
        samples=dataset_smote,
        label_column_index_or_name=column_selection,
        smote_percent=0,
        neighbors=1,
        seed=0)

    assert output_dt == dataset_smote


def test_category_column_type(dataset_smote_with_string):
    # Test the datatable with illegal column type

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    SMOTEModule._run_impl(
        samples=dataset_smote_with_string,
        label_column_index_or_name=column_selection,
        smote_percent=100,
        neighbors=1,
        seed=0)


def test_empty_dataset(dataset_table_null):
    # Test the datatable with zero row
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    with pytest.raises(error_setting.TooFewRowsInDatasetError):
        SMOTEModule._run_impl(
            samples=dataset_table_null,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=1,
            seed=0)


def test_multi_class(dataset_smote_with_multi_class):
    # Test the datatable with multiple class

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    with pytest.raises(error_setting.NotExpectedLabelColumnError):
        SMOTEModule._run_impl(
            samples=dataset_smote_with_multi_class,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=1,
            seed=0)


def test_feature_columns_num(dataset_smote_with_no_feature_column):
    # Test the datatable with no feature columns

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('class').build()

    with pytest.raises(error_setting.TooFewFeatureColumnsInDatasetError):
        SMOTEModule._run_impl(
            samples=dataset_smote_with_no_feature_column,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=1,
            seed=0)


def test_target_columns_num(dataset_smote):
    # Test the datatable with no target column

    column_selection = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.LABEL).build()

    with pytest.raises(error_setting.UnexpectedNumberOfColumnsError):
        SMOTEModule._run_impl(
            samples=dataset_smote,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=1,
            seed=0)


def test_smote_on_missing_value(dataset_smote: DataTable):
    row = dataset_smote.number_of_rows
    columns = dataset_smote.number_of_columns
    pos_x = np.random.randint(0, row)
    pos_y = np.random.randint(0, columns)
    data = dataset_smote.get_data_frame()
    data.iloc[pos_x, pos_y] = np.nan
    data_table = DataTable(data)
    column_selection = DataTableColumnSelectionBuilder().include_col_names('class').build()
    with pytest.raises(error_setting.InvalidDatasetError,
                       match='Consider using the Clean Missing Data module to remove missing values.'):
        SMOTEModule._run_impl(
            samples=data_table,
            label_column_index_or_name=column_selection,
            smote_percent=100,
            neighbors=1,
            seed=0)

import pytest
import pandas as pd
import numpy as np
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import InvalidColumnCategorySelectedError, ColumnNotFoundError, \
    TooFewColumnsInDatasetError
from azureml.studio.modules.datatransform.manipulation.convert_to_indicator_values.convert_to_indicator_values import \
    ConvertToIndicatorValuesModule
from azureml.studio.modules.datatransform.manipulation.metadata_editor.metadata_editor \
    import MetadataEditorDataType, MetadataEditorCategorical, \
    MetadataEditorFlag, MetadataEditorModule


@pytest.fixture
def input_data_table():
    dt = DataTable(pd.DataFrame({
        'f0': [0, 3, 6],
        'f1': ['b', 'd', 'a'],
        'f2': [2, 3, np.nan],
        }))
    return dt


@pytest.fixture
def input_dt_categorical_feature(input_data_table):
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["f1", "f2"],"exclude":false}]}')
    new_data_type = MetadataEditorDataType.Unchanged
    new_categorical = MetadataEditorCategorical.Categorical
    new_field = MetadataEditorFlag.Features
    # pylint: disable=no-value-for-parameter
    return MetadataEditorModule.run(
        table=input_data_table,
        column_select=col_select,
        new_data_type=new_data_type,
        new_categorical=new_categorical,
        new_field=new_field,
    )[0]


@pytest.fixture
def input_dt_categorical_label(input_data_table):
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["f1"],"exclude":false}]}')
    new_data_type = MetadataEditorDataType.Unchanged
    new_categorical = MetadataEditorCategorical.Categorical
    new_field = MetadataEditorFlag.Labels
    new_col_name = 'cf1'
    # pylint: disable=no-value-for-parameter
    return MetadataEditorModule.run(
        table=input_data_table,
        column_select=col_select,
        new_data_type=new_data_type,
        new_categorical=new_categorical,
        new_field=new_field,
        new_column_names=new_col_name
    )[0]


@pytest.fixture
def output_data_table():
    dt = DataTable(pd.DataFrame({
        'f0': [0, 3, 6],
        'f1': pd.Series(['b', 'd', 'a']).astype('category'),
        'f2': pd.Series([2, 3, np.nan]).astype('category'),
        'f1-a': [0.0, 0.0, 1.0],
        'f1-b': [1.0, 0.0, 0.0],
        'f1-d': [0.0, 1.0, 0.0],
        'f2-#NAN': [0.0, 0.0, 1.0],
        'f2-2.0': [1.0, 0.0, 0.0],
        'f2-3.0': [0.0, 1.0, 0.0],
        }))
    return dt


@pytest.fixture
def output_dt_categorical_label():
    dt = DataTable(pd.DataFrame({
        'f0': [0, 3, 6],
        'cf1': pd.Series(['b', 'd', 'a']).astype('category'),
        'f2': [2, 3, np.nan],
        'cf1-a': [0.0, 0.0, 1.0],
        'cf1-b': [1.0, 0.0, 0.0],
        'cf1-d': [0.0, 1.0, 0.0],
        }))
    return dt


def test_run_success(input_dt_categorical_feature, output_data_table):
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["f1","f2"],"exclude":false}]}')
    # pylint: disable=no-value-for-parameter
    result, = ConvertToIndicatorValuesModule.run(
        table=input_dt_categorical_feature,
        column_select=col_select,
    )
    assert result.data_frame.equals(output_data_table.data_frame)
    assert result.meta_data.column_attributes == output_data_table.meta_data.column_attributes


def test_categorical_label_should_not_be_feature_or_label(input_dt_categorical_label, output_dt_categorical_label):
    # Label field categorical columns should not be considered as feature based on V1
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["cf1"],"exclude":false}]}')
    # pylint: disable=no-value-for-parameter
    result, = ConvertToIndicatorValuesModule.run(
        table=input_dt_categorical_label,
        column_select=col_select,
    )
    assert result.data_frame.equals(output_dt_categorical_label.data_frame)
    for col_index in range(result.data_frame.shape[1]):
        col_name = result.data_frame.columns[col_index]
        if col_name.startswith("cf1-"):
            assert not result.meta_data.column_attributes[col_index].is_feature
            assert col_name != result.meta_data.label_column_name


def test_overwrite_feature_col(input_dt_categorical_feature):
    # Overwritten columns and their meta data should be removed in output
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["f1", "f2"],"exclude":false}]}')
    result, = ConvertToIndicatorValuesModule.run(
        table=input_dt_categorical_feature,
        column_select=col_select,
        overwrite=True
    )
    assert 'f1' not in result.data_frame.columns
    assert 'f2' not in result.data_frame.columns


def test_overwrite_label_col(input_dt_categorical_label):
    # Overwritten columns and their meta data should be removed in output
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["cf1"],"exclude":false}]}')
    result, = ConvertToIndicatorValuesModule.run(
        table=input_dt_categorical_label,
        column_select=col_select,
        overwrite=True
    )
    assert 'cf1' not in result.data_frame.columns
    assert result.meta_data.label_column_name is None


def test_error_selected_col_not_categorical(input_dt_categorical_feature):
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["f0", "f1"],"exclude":false}]}')
    with pytest.raises(InvalidColumnCategorySelectedError,
                       match='Column with name "f0" is not'):
        ConvertToIndicatorValuesModule.run(
            table=input_dt_categorical_feature,
            column_select=col_select,
            overwrite=True
        )


def test_error_selected_col_not_found(input_dt_categorical_feature):
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["aaa"],"exclude":false}]}')
    with pytest.raises(ColumnNotFoundError,
                       match='Column with name or index "aaa" not found'):
        ConvertToIndicatorValuesModule.run(
            table=input_dt_categorical_feature,
            column_select=col_select,
            overwrite=True
        )


def test_error_too_few_columns_in_dataset():
    df = pd.DataFrame()
    dt = DataTable(df)
    col_select = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["col0"],"exclude":false}]}')
    with pytest.raises(
            TooFewColumnsInDatasetError,
            match='Number of columns in input dataset "Dataset" is less than allowed minimum of 1 column'):
        ConvertToIndicatorValuesModule.run(
            table=dt,
            column_select=col_select,
            overwrite=True
        )

import pandas as pd
import pytest

import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.text_analytics.feature_hashing.feature_hashing import FeatureHashingModule


@pytest.fixture
def data_table_with_text():
    df = pd.DataFrame()
    df['text'] = [
        '"Ok~ but I think the Keirsey Temperment Test is more accurate - and cheaper.',
        't describe you at all. This messes up the results, and it did not describe me very well.']
    df['text2'] = [
        '"Ok~ but I think the Keirsey Temperment Test is more accurate',
        't describe you at all. This messes up the results, and it did not describe me very well.']

    return DataTable(df)


@pytest.fixture
def data_table_with_numeric():
    df = pd.DataFrame()
    df['text'] = [1, 2, 3]
    df['text2'] = [2, 3, 4]

    return DataTable(df)


@pytest.mark.parametrize('data_table_null', [
    DataTable(),
    DataTable(pd.DataFrame(
        {
            'text': [],
            'text2': []
        }
    ))
])
def test_empty_dataset(data_table_null):
    # Test the datatable with zero row

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().build()

    with pytest.raises(error_setting.TooFewRowsInDatasetError):
        FeatureHashingModule.run(
            dataset=data_table_null,
            target_column=column_selection,
            bits=5,
            ngrams=2)


def test_column_type_not_str(data_table_with_numeric):
    # Test the datatable which has several column types

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().build()

    with pytest.raises(error_setting.InvalidColumnTypeError):
        FeatureHashingModule.run(
            dataset=data_table_with_numeric,
            target_column=column_selection,
            bits=5,
            ngrams=2)


def test_run(data_table_with_text):
    # Test the correct datatable

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().build()

    output_dt, = FeatureHashingModule.run(
        dataset=data_table_with_text,
        target_column=column_selection,
        bits=2,
        ngrams=2)

    actual_column_names = ['text', 'text2', 'text_HashingFeature.0', 'text_HashingFeature.1', 'text_HashingFeature.2',
                           'text_HashingFeature.3', 'text2_HashingFeature.0', 'text2_HashingFeature.1',
                           'text2_HashingFeature.2', 'text2_HashingFeature.3']
    expected_column_names = output_dt.data_frame.columns.values.tolist()

    assert actual_column_names == expected_column_names


def test_exceeded_hashed_feature_column_size_generated(data_table_with_text):
    # Test the datatable with exceeded hashed feature column size generated

    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().build()

    with pytest.raises(error_setting.ExceedsColumnLimitError):
        FeatureHashingModule.run(
            dataset=data_table_with_text,
            target_column=column_selection,
            bits=30,
            ngrams=2)

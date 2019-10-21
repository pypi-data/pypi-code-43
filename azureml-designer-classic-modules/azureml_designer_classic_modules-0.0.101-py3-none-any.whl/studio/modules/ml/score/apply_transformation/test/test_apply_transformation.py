import pytest
import pandas as pd
import numpy as np

from azureml.studio.modules.ml.score.apply_transformation.apply_transformation \
    import ApplyTransformationModule
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.datatransform.clean_missing_data.clean_missing_transform \
    import CleanMissingValueTransform, CleanMissingDataHandlingPolicy


def validate_meta_data(compute_meta_data, expect_meta_data):
    assert compute_meta_data.column_attributes == expect_meta_data.column_attributes
    assert compute_meta_data.score_column_names == expect_meta_data.score_column_names
    assert compute_meta_data.label_column_name == expect_meta_data.label_column_name
    assert compute_meta_data.feature_channels == expect_meta_data.feature_channels


def validate_data_table(compute_dt, expect_dt):
    # Validate data frame
    assert compute_dt.data_frame.equals(expect_dt.data_frame)
    validate_meta_data(compute_dt.meta_data, expect_dt.meta_data)


@pytest.fixture
def data_table():
    df = pd.DataFrame()
    df['col0'] = [2, 1, 10]
    df['col1'] = [np.nan, 1.6, 1]
    df['col2'] = [np.nan, 'a', 'b']
    df['col3'] = [None, True, False]
    df['col4'] = [None, np.nan, None]
    return DataTable(df)


@pytest.fixture
def transform(data_table):
    return CleanMissingValueTransform(
        cleaning_mode=CleanMissingDataHandlingPolicy.ReplaceWithValue,
        replacement_value='0',
        remove_columns_with_all_missing=True,
        indicator_columns=True,
        column_names=data_table.column_names,
        min_ratio=0,
        max_ratio=1)


def test_run(data_table, transform):
    compute_dt = ApplyTransformationModule.run(
        transform=transform,
        data=data_table)[0]

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

import os
import pytest
import pandas as pd
import numpy as np

from azureml.studio.core.utils.jsonutils import load_json_file
from azureml.studio.core.data_frame_schema import DataFrameSchema, FeatureChannel


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def input_data_frame_simple():
    df = pd.DataFrame()
    df['apple'] = [1, 2, 3, 4, 5]
    df['price'] = [2, 4, 6, 8, 10]
    return df


@pytest.fixture()
def input_data_frame_multi_types():
    df = pd.DataFrame()
    df['int'] = [1, 10, np.nan]
    df['float'] = [1.6, 1, np.nan]
    df['string'] = ['3', '1', np.nan]
    df['bool'] = [True, np.nan, False]
    df['category'] = pd.Series([2, 1, 3]).astype('category')
    df['datetime'] = pd.to_datetime(
        arg=pd.Series(['20190101', '20190103', np.nan]), format='%Y%m%d', errors='coerce')
    df['nan'] = [np.nan, np.nan, np.nan]
    return df


@pytest.fixture()
def expect_json_simple():
    return load_json_file(os.path.join(script_directory(), 'dataset_simple.schema'))


@pytest.fixture()
def expect_json_multi_types():
    return load_json_file(os.path.join(script_directory(), 'dataset_multi_types.schema'))


@pytest.fixture()
def compute_json_multi_types(input_data_frame_multi_types):
    df = input_data_frame_multi_types

    column_attributes = DataFrameSchema.generate_column_attributes(df)

    feature_channels = {
        'Channel0': FeatureChannel(
            name='Channel0',
            is_normalized=True,
            feature_column_names=[df.columns[2], df.columns[3]])
    }
    schema = DataFrameSchema(
        column_attributes=column_attributes,
        score_column_names={'numeric_score': df.columns[0]},
        label_column_name={'True Labels': df.columns[1]},
        feature_channels=feature_channels
    )
    return schema.to_dict()


@pytest.fixture()
def compute_json_simple(input_data_frame_simple):
    df = input_data_frame_simple

    column_attributes = DataFrameSchema.generate_column_attributes(df)

    schema = DataFrameSchema(
        column_attributes=column_attributes
    )
    return schema.to_dict()


def test_to_json_multi_types(compute_json_multi_types, expect_json_multi_types):
    assert compute_json_multi_types == expect_json_multi_types


def test_to_json_simple(compute_json_simple, expect_json_simple):
    assert compute_json_simple == expect_json_simple

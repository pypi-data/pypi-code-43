import pytest
import json
import pandas as pd
import numpy as np

from azureml.studio.common.datatable.data_table_constructor import DataFrameSchemaConstructor, DataTableConstructor
from azureml.studio.core.data_frame_schema import DataFrameSchema, FeatureChannel
from azureml.studio.common.datatable.data_table import DataTable


@pytest.fixture()
def meta_data_dict():
    meta_data_json = \
        (
            '{'
            '\"columnAttributes\": '
            '['
            '    {\"name\":\"col0\",\"type\":\"Numeric\",\"isFeature\":true,'
            '     \"elementType\":{\"typeName\":\"int64\",\"isNullable\":false}},'
            '    {\"name\":\"col1\",\"type\":\"Numeric\",\"isFeature\":true,'
            '     \"elementType\":{\"typeName\":\"float64\",\"isNullable\":false}},'
            '    {\"name\":\"col2\",\"type\":\"String\",\"isFeature\":true,'
            '     \"elementType\":{\"typeName\":\"str\",\"isNullable\":false}},'
            '    {\"name\":\"col3\",\"type\":\"Binary\",\"isFeature\":true,'
            '     \"elementType\":{\"typeName\":\"bool\",\"isNullable\":false}},'
            '    {\"name\":\"col4\",\"type\":\"Categorical\",\"isFeature\":true,'
            '     \"elementType\":{\"typeName\":\"category\",\"isNullable\":false}}'
            '],'
            '\"scoreColumns\":{"Assigned Labels": "col0", "Calibrated Score": "col1"},'
            '\"labelColumns\":{"True Labels": "col2"},'
            '\"featureChannels\":[{"name": "Binary Classification Scores",'
            ' "isNormalized": true, "featureColumns":["col3","col4"]}]'
            '}'
        )
    return json.loads(meta_data_json)


meta_data_json_string = '''
{
    "columnAttributes": [
        {
            "name": "int",
            "type": "Numeric",
            "isFeature": false,
            "elementType": {
                "typeName": "float64",
                "isNullable": false
            }
        },
        {
            "name": "float",
            "type": "Numeric",
            "isFeature": false,
            "elementType": {
                "typeName": "float64",
                "isNullable": false
            }
        },
        {
            "name": "string",
            "type": "String",
            "isFeature": true,
            "elementType": {
                "typeName": "str",
                "isNullable": false
            }
        },
        {
            "name": "bool",
            "type": "Binary",
            "isFeature": true,
            "elementType": {
                "typeName": "bool",
                "isNullable": false
            }
        },
        {
            "name": "category",
            "type": "Categorical",
            "isFeature": true,
            "elementType": {
                "typeName": "category",
                "isNullable": false
            }
        },
        {
            "name": "datetime",
            "type": "DateTime",
            "isFeature": true,
            "elementType": {
                "typeName": "datetime64",
                "isNullable": false
            }
        },
        {
            "name": "nan",
            "type": "NAN",
            "isFeature": true,
            "elementType": {
                "typeName": "NAN",
                "isNullable": false
            }
        }
    ],
    "scoreColumns": {"numeric_score": "int"},
    "labelColumns": {"True Labels": "float"},
    "featureChannels": [{"name": "Channel0", "isNormalized": true, "featureColumns": ["string", "bool"]}]
}'''
@pytest.fixture()
def expect_json_multi_types():
    return json.loads(meta_data_json_string)


@pytest.fixture
def data_frame():
    df = pd.DataFrame()
    df['col0'] = [2, 1, 10]
    df['col1'] = [np.nan, 1.6, 1]
    df['col2'] = [np.nan, 'a', 'b']
    df['col3'] = [None, True, False]
    df['col4'] = pd.Series([np.nan, 'c', 'f']).astype('category')
    return df


@pytest.fixture
def column_attributes(data_frame):
    attributes = DataFrameSchema.generate_column_attributes(data_frame)
    return attributes


@pytest.fixture
def feature_channels():
    feature_channel = FeatureChannel(name='Binary Classification Scores',
                                     is_normalized=True, feature_column_names=['col3', 'col4'])
    return {'Binary Classification Scores': feature_channel}


@pytest.fixture
def data_dict(data_frame):
    d = dict()
    for col_index in range(5):
        col_name = data_frame.columns.tolist()[col_index]
        column = list(data_frame.iloc[:, col_index])
        d.update({col_name: column})
    return d


def test_create_data_table_schema_from_dict(meta_data_dict, data_frame, column_attributes, feature_channels):
    schema = DataFrameSchemaConstructor.create_data_table_schema_from_dict(meta_data_dict)

    assert not schema.column_attributes[0].is_feature
    assert not schema.column_attributes[1].is_feature
    assert not schema.column_attributes[2].is_feature
    assert schema.column_attributes == column_attributes
    assert schema.score_column_names == {'Assigned Labels': 'col0', 'Calibrated Score': 'col1'}
    assert schema.label_column_name == 'col2'
    assert schema._score_columns == {'Assigned Labels': 0, 'Calibrated Score': 1}
    assert schema._label_columns == {'True Labels': 2}
    assert schema.feature_channels.keys() == feature_channels.keys()
    feature_channel = list(schema.feature_channels.values())[0]
    feature_channel_compare = list(feature_channels.values())[0]
    assert feature_channel.name == feature_channel_compare.name
    assert feature_channel.is_normalized == feature_channel_compare.is_normalized
    assert feature_channel.feature_column_names == feature_channel_compare.feature_column_names


def test_create_data_table_from_dict(data_dict, data_frame, meta_data_dict, column_attributes):
    data_table = DataTableConstructor.create_data_table_from_dict(data_dict, meta_data_dict)
    assert data_table.data_frame.equals(data_frame)
    assert data_table.meta_data.column_attributes == column_attributes


def test_construct_data_table_with_self_generated_schema(data_dict, data_frame):
    data_table_origin = DataTable(data_frame)
    self_generated_schema_dict = data_table_origin.meta_data.to_dict()

    data_table_recovered = DataTableConstructor.create_data_table_from_dict(data_dict, self_generated_schema_dict)

    assert data_table_recovered.data_frame.equals(data_table_origin.data_frame)
    assert data_table_recovered.meta_data.column_attributes == data_table_origin.meta_data.column_attributes


def test_with_multi_types(expect_json_multi_types):
    # Smoke test, to test if multi-type input data can be used for constructing DataTable
    input_data_dict = {
        'int': 1,
        'float': 1.6,
        'string': 'apple',
        'bool': True,
        'category': 2,
        'datetime': '2019-01-01 00:00:00',
        'nan': np.nan
    }
    meta_data_dict = expect_json_multi_types

    dt = DataTableConstructor.create_data_table_from_dict(input_data_dict, meta_data_dict)
    assert dt

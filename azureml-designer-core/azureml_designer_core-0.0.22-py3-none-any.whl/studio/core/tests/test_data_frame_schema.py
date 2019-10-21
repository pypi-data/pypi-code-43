import pandas as pd
import pytest
import json
from datetime import timedelta

from azureml.studio.core.data_frame_schema import DataFrameSchema, ColumnTypeName, ElementTypeName, \
    ColumnAttribute
from azureml.studio.core.utils.labeled_list import LabeledList


@pytest.fixture
def simple_data_frame():
    return pd.DataFrame({'float': [1.0, 2.0],
                         'int': [1, 2],
                         'datetime': [pd.Timestamp('20180310'), pd.Timestamp('20190910')],
                         'string': ['foo', 'bar'],
                         'bool': [True, False],
                         'timespan': [timedelta(), timedelta()],
                         'category': pd.Series(['a', 3]).astype('category'),
                         })


@pytest.fixture
def simple_data_frame_schema(simple_data_frame):
    return DataFrameSchema.from_data_frame(df=simple_data_frame)


@pytest.fixture
def schema_data(request):
    filename = request.module.__file__.replace('test_data_frame_schema.py', 'sample.schema')
    with open(filename) as fin:
        return json.load(fin)


def test_json_to_schema_to_json(schema_data):
    schema = DataFrameSchema.from_dict(schema_data)
    new_data = schema.to_dict()
    assert schema_data == new_data


def test_df_to_schema(simple_data_frame):
    df = simple_data_frame
    df_json_data = DataFrameSchema.data_frame_to_dict(df)
    attributes = df_json_data['columnAttributes']
    assert len(attributes) == len(df.columns)


def test_empty_df():
    empty_df = pd.DataFrame(columns=['a', 'b', 'c'])
    for attr in DataFrameSchema.data_frame_to_dict(empty_df)['columnAttributes']:
        assert attr['type'] == 'NAN'


def test_copy(simple_data_frame_schema):
    assert simple_data_frame_schema.copy() is simple_data_frame_schema
    assert simple_data_frame_schema.copy(if_clone=True) is not simple_data_frame_schema


def test_select_columns(simple_data_frame_schema):
    schema_new = simple_data_frame_schema.select_columns([0, 1])
    assert schema_new.column_attributes[0] == simple_data_frame_schema.column_attributes[0]
    assert schema_new.column_attributes[1] == simple_data_frame_schema.column_attributes[1]


def test_compute_attributes_from_columns():
    with pytest.raises(TypeError, match='Argument "df": Not Dataframe'):
        DataFrameSchema.generate_column_attributes([1, 2, 3])


def test_compute_column_attributes_from_columns(simple_data_frame):
    column_attributes = DataFrameSchema.generate_column_attributes(simple_data_frame)
    assert column_attributes[0].column_type == ColumnTypeName.NUMERIC
    assert column_attributes[1].column_type == ColumnTypeName.NUMERIC
    assert column_attributes[2].column_type == ColumnTypeName.DATETIME
    assert column_attributes[3].column_type == ColumnTypeName.STRING
    assert column_attributes[4].column_type == ColumnTypeName.BINARY
    assert column_attributes[5].column_type == ColumnTypeName.TIMESPAN
    assert column_attributes[6].column_type == ColumnTypeName.CATEGORICAL

    assert column_attributes[0].element_type == ElementTypeName.FLOAT
    assert column_attributes[1].element_type == ElementTypeName.INT
    assert column_attributes[2].element_type == ElementTypeName.DATETIME
    assert column_attributes[3].element_type == ElementTypeName.STRING
    assert column_attributes[4].element_type == ElementTypeName.BOOL
    assert column_attributes[5].element_type == ElementTypeName.TIMESPAN
    assert column_attributes[6].element_type == ElementTypeName.CATEGORY


def test_compute_column_attributes_with_zero_rows():
    df = pd.DataFrame(columns=['col0'])
    column_attributes = DataFrameSchema.generate_column_attributes(df)
    assert column_attributes[0].name == 'col0'
    assert column_attributes[0].column_type == ColumnTypeName.NAN
    assert column_attributes[0].element_type == ElementTypeName.NAN


def test_compute_column_attributes_with_zero_columns():
    df = pd.DataFrame(index=[1])
    column_attributes = DataFrameSchema.generate_column_attributes(df)
    assert column_attributes == LabeledList()


def test_compute_column_attributes_with_empty_data_frame():
    df = pd.DataFrame()
    column_attributes = DataFrameSchema.generate_column_attributes(df)
    assert column_attributes == LabeledList()


def test_get_column_element_type_from_column():
    with pytest.raises(TypeError, match='Column type is not Pandas.Series.'):
        DataFrameSchema.get_column_element_type([1, 2, 3])


def test_change_column_attribute(simple_data_frame_schema):
    column = pd.Series(['a', 'b', 'c'])
    col_key = 'float'
    simple_data_frame_schema.set_column_attribute(col_key, column)
    assert simple_data_frame_schema.get_column_attribute(col_key).column_type == ColumnTypeName.STRING
    assert simple_data_frame_schema.get_column_attribute(col_key).element_type == ElementTypeName.STRING
    assert simple_data_frame_schema.get_column_attribute(col_key).is_feature
    assert simple_data_frame_schema.get_column_attribute(col_key).name == col_key
    with pytest.raises(TypeError, match='Column type is not Pandas.Series.'):
        simple_data_frame_schema.set_column_attribute(0, [1, 2, 3])


def test_score_column_name(simple_data_frame_schema):
    simple_data_frame_schema.score_column_names = {'score_type1': 'float'}
    simple_data_frame_schema.score_column_names = {'score_type2': 'int'}
    assert simple_data_frame_schema.score_column_names == {'score_type1': 'float', 'score_type2': 'int'}
    with pytest.raises(
            TypeError,
            match='Argument "type_key_dict": Score column must be set by a dictionary'
    ):
        simple_data_frame_schema.score_column_names = 'string'


def test_remove_score_column(simple_data_frame_schema):
    simple_data_frame_schema.score_column_names = {'score_type1': 'float'}
    simple_data_frame_schema.score_column_names = {'score_type2': 'int'}
    del simple_data_frame_schema.score_column_names
    assert not simple_data_frame_schema.score_column_names


def test_label_column_name(simple_data_frame_schema):
    simple_data_frame_schema.label_column_name = 'int'
    assert simple_data_frame_schema.label_column_name == 'int'
    assert not simple_data_frame_schema.get_column_attribute('int').is_feature
    simple_data_frame_schema.label_column_name = 0
    assert simple_data_frame_schema.label_column_name == 'float'
    with pytest.raises(
            TypeError,
            match=f'Argument "col_key_or_type_key_dict": Label column must be set by a dictionary'
            f' or by column name or index.'
    ):
        simple_data_frame_schema.label_column_name = list()


def test_remove_label_column(simple_data_frame_schema):
    simple_data_frame_schema.label_column_name = 'string'
    del simple_data_frame_schema.label_column_name
    assert not simple_data_frame_schema.label_column_name


def test_validate(simple_data_frame_schema, simple_data_frame):
    simple_data_frame_schema.validate(simple_data_frame)

    one_more_column_data_frame = simple_data_frame.assign(new_float=[5.1, 6.2])
    with pytest.raises(
            ValueError,
            match='Attributes "meta_data" do not match with Dataframe "df".'
    ):
        simple_data_frame_schema.validate(one_more_column_data_frame)

    two_column_data_frame = simple_data_frame[['float', 'int']]
    with pytest.raises(
            ValueError,
            match='Attributes "meta_data" do not match with Dataframe "df".'
    ):
        simple_data_frame_schema.validate(two_column_data_frame)

    zero_row_data_frame = pd.DataFrame()
    with pytest.raises(
            ValueError,
            match='Attributes "meta_data" do not match with Dataframe "df".'
    ):
        simple_data_frame_schema.validate(zero_row_data_frame)


def test_set_column_name(simple_data_frame_schema):
    col_key = 0
    new_col_name = 'col_1'
    simple_data_frame_schema.set_column_name(col_key, new_col_name)
    assert simple_data_frame_schema.column_attributes.names[0] == new_col_name
    assert simple_data_frame_schema.column_attributes[0].name == new_col_name


def test_copy_with_attributes(simple_data_frame_schema):
    schema_new = simple_data_frame_schema.copy()
    assert schema_new is simple_data_frame_schema
    schema_new = simple_data_frame_schema.copy(if_clone=True)
    assert schema_new is not simple_data_frame_schema
    assert schema_new.column_attributes == simple_data_frame_schema.column_attributes


def test_set_column_as_feature(simple_data_frame_schema):
    col_key = 0
    simple_data_frame_schema.score_column_names = {'score_type': col_key}
    assert not simple_data_frame_schema.get_column_attribute(col_key).is_feature
    simple_data_frame_schema.label_column_name = col_key
    assert not simple_data_frame_schema.get_column_attribute(col_key).is_feature
    simple_data_frame_schema.set_column_as_feature(col_key)
    assert simple_data_frame_schema.get_column_attribute(col_key).is_feature


def test_select_columns_with_label_and_score(simple_data_frame_schema, simple_data_frame):
    col_keys = [1, 2]
    schema_selected = simple_data_frame_schema.select_columns(col_keys)
    assert schema_selected.column_attributes == \
        DataFrameSchema.from_data_frame(simple_data_frame.iloc[:, col_keys]).column_attributes
    simple_data_frame_schema.label_column_name = 1
    simple_data_frame_schema.score_column_names = {'score_type': 2}
    schema_selected = simple_data_frame_schema.select_columns(col_keys)
    assert schema_selected.label_column_name == 'int'
    assert schema_selected.score_column_names == {'score_type': 'datetime'}


def test_column_attribute_equals():
    col_attribute = ColumnAttribute()
    with pytest.raises(TypeError, match='Argument "other": Not column attribute.'):
        col_attribute == 'a'

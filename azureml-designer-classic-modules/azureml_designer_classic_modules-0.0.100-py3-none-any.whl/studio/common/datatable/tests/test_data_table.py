import pytest
import pandas as pd
import numpy as np

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, load_data_frame_from_directory
from azureml.studio.core.utils.labeled_list import LabeledList
from azureml.studio.core.logger import TimeProfile
from azureml.studio.common.datatable.constants import ColumnTypeName, ElementTypeName
from pandas.core.dtypes.common import is_float_dtype


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


@pytest.fixture
def empty_data_frame():
    return pd.DataFrame()


@pytest.fixture
def data_frame_with_all_nan_column():
    df = pd.DataFrame()
    df['col0'] = [np.nan, None]
    df['col1'] = [np.nan, 1.6]
    return df


@pytest.fixture
def data_table(data_frame):
    return DataTable(data_frame)


@pytest.fixture
def meta_data(data_frame):
    column_attributes = DataFrameSchema.generate_column_attributes(data_frame)
    return DataFrameSchema(column_attributes=column_attributes)


class TestDataTable:

    def test__init__(self, data_frame):
        with pytest.raises(TypeError, match='Argument "df": Not Dataframe'):
            DataTable([1, 2, 3])

        with pytest.raises(TypeError, match='Argument "meta_data": Invalid metadata type'):
            DataTable(data_frame, [1, 2, 3])

    def test__init__with_empty_dataframe_no_meta(self, empty_data_frame):
        dt = DataTable(empty_data_frame)
        assert dt.data_frame.equals(empty_data_frame)
        assert dt.meta_data.column_attributes == LabeledList()
        assert dt.meta_data.score_column_names == dict()
        assert dt.meta_data.label_column_name is None
        assert dt.meta_data.feature_channels == dict()

    def test__init__with_zero_row_dataframe(self):
        df = pd.DataFrame(columns=['col0', 'col1'])
        dt = DataTable(df)
        assert dt.data_frame.equals(df)
        assert dt.meta_data.score_column_names == dict()
        assert dt.meta_data.label_column_name is None
        assert dt.meta_data.feature_channels == dict()
        assert dt.number_of_columns == 2
        assert dt.number_of_rows == 0
        assert dt.get_element_type(0) == ElementTypeName.NAN
        assert dt.get_column_type(0) == ColumnTypeName.NAN

    def test__init__with_zero_row_dataframe_non_zero_meta(self, empty_data_frame):
        df_for_meta = pd.DataFrame({'col0': [1, 2, 3]})
        non_zero_meta = DataFrameSchema(DataFrameSchema.generate_column_attributes(df=df_for_meta))
        with pytest.raises(ValueError):
            DataTable(empty_data_frame, non_zero_meta)

    def test__init__with_zero_column_dataframe(self):
        df = pd.DataFrame(index=[0, 1])
        dt = DataTable(df)
        assert dt.data_frame.equals(df)
        assert dt.meta_data.score_column_names == dict()
        assert dt.meta_data.label_column_name is None
        assert dt.meta_data.feature_channels == dict()
        assert dt.number_of_rows == 2
        assert dt.number_of_columns == 0
        with pytest.raises(
                KeyError,
                match='Argument "key" is out of range from 0 to -1.'
        ):
            dt.get_element_type(0)
            dt.get_column_type(0)
            dt.get_column(0)

    def test__init__with_dataframe_with_all_nan_column(self, data_frame_with_all_nan_column, meta_data):
        column_attributes_with_two_column = LabeledList()
        column_attributes_with_two_column.append(meta_data.column_attributes[0].name, meta_data.column_attributes[0])
        column_attributes_with_two_column.append(meta_data.column_attributes[1].name, meta_data.column_attributes[1])

        meta_data_with_two_columns = DataFrameSchema(column_attributes_with_two_column)

        dt = DataTable(data_frame_with_all_nan_column, meta_data_with_two_columns)
        assert dt.meta_data.column_attributes == meta_data_with_two_columns.column_attributes
        assert dt.data_frame.equals(data_frame_with_all_nan_column)

    # To fix bug 469279
    def test__init__with_dataframe_has_array_element(self):
        df = pd.DataFrame(columns=['col0', 'col1', 'col2', 'col3', 'col4'])
        df['col0'] = [[1, 2], [3, 4]]
        df['col1'] = [np.array([1, 2]), np.array([3, 4])]
        df['col2'] = [pd.Series([1, 2]), pd.Series([3, 4])]
        df['col3'] = [{'apple': 1}, {'banana': 2}]
        df['col4'] = [pd.DataFrame({'a': [1]}), pd.DataFrame({'b': [2]})]
        dt = DataTable(df)
        assert dt.data_frame is df

    # To fix bug 487721
    def test__init__with_dataframe_has_nat(self):
        df = pd.DataFrame({'col0': [pd.NaT, None, np.nan, 4.5]})
        DataTable(df)

    # To fix bug 487834
    def test_recursive__init__with_dataframe_has_nat(self):
        df = pd.DataFrame({'col': [pd.NaT, 123, 456, 789]})
        dt1 = DataTable(df)
        DataTable(dt1.data_frame, dt1.meta_data)

    # To fix bug 507636
    def test__init__with_numeric_schema_while_dataframe_has_only_none(self):
        df = pd.DataFrame({'col0': [None]})
        df_for_meta_data = pd.DataFrame({'col0': [1.0]})
        meta_data = DataFrameSchema(column_attributes=DataFrameSchema.generate_column_attributes(df=df_for_meta_data))
        dt = DataTable(df, meta_data)
        assert dt.get_element_type('col0') == ElementTypeName.FLOAT

    def test_name(self, data_table):
        data_table.name = 'data table'
        assert data_table.name == 'data table'

    def test_number_of_columns(self, data_table, data_frame):
        assert data_table.number_of_columns == data_frame.shape[1]

    def test_number_of_rows(self, data_table, data_frame):
        assert data_table.number_of_rows == data_frame.shape[0]

    def test_data_frame(self, data_table, data_frame):
        assert data_table.data_frame is data_frame

    def test_meta_data(self, data_frame, meta_data):
        assert DataTable(data_frame, meta_data).meta_data is meta_data

    def test_column_names(self, data_table, data_frame):
        assert data_table.column_names == list(data_frame.columns)

    def test_get_meta_data(self, data_frame, meta_data):
        assert DataTable(data_frame, meta_data).get_meta_data() is not meta_data
        assert not DataTable(data_frame).get_meta_data().validate(data_frame)

    def test_get_data_frame(self, data_frame):
        assert DataTable(data_frame).get_data_frame() is not data_frame
        assert DataTable(data_frame).get_data_frame(if_clone=False) is not data_frame

    def test_get_column_index(self, data_table, data_frame):
        assert data_table.get_column_index(['col1', 'col2']) == [1, 2]
        assert data_table.get_column_index('col3') == 3

    def test_get_column_type(self, data_table):
        assert data_table.get_column_type(0) == ColumnTypeName.NUMERIC
        assert data_table.get_column_type(1) == ColumnTypeName.NUMERIC
        assert data_table.get_column_type(2) == ColumnTypeName.STRING
        assert data_table.get_column_type('col3') == ColumnTypeName.BINARY

    def test_get_element_type(self, data_table):
        assert data_table.get_element_type(0) == ElementTypeName.INT
        assert data_table.get_element_type(1) == ElementTypeName.FLOAT
        assert data_table.get_element_type(2) == ElementTypeName.STRING
        assert data_table.get_element_type('col3') == ElementTypeName.BOOL

    def test_get_slice_by_column_indexes(self, data_table, data_frame):
        data_table_new = data_table.get_slice_by_column_indexes([0, 1])
        assert data_table_new.get_data_frame().equals(data_frame.iloc[:, 0:2])
        assert not data_table_new.get_meta_data().validate(data_frame.iloc[:, 0:2])

        data_table_new = data_table.get_slice_by_column_indexes([1])
        assert data_table_new.get_data_frame().equals(data_frame.iloc[:, [1]])
        assert not data_table_new.get_meta_data().validate(data_frame.iloc[:, 1].to_frame())

    def test_get_column(self, data_table, data_frame):
        assert data_table.get_column('col1').equals(data_frame['col1'])
        assert data_table.get_column(1).equals(data_frame.iloc[:, 1])

    def test_set_column(self, data_table, data_frame):
        column = pd.Series(['a', 'b', 'c'])
        col_key = 'col1'
        data_table.set_column(col_key, column)
        assert data_table.get_column(col_key).equals(column)
        assert data_table.meta_data.column_attributes[col_key] == \
            DataFrameSchema.generate_column_attribute(column, col_key)
        with pytest.raises(TypeError, match='Column "col1": Column type is not Pandas.Series'):
            data_table.set_column(col_key, [3, 2, 1])
        with pytest.raises(
                ValueError,
                match='Argument "column": Row number does not match. Expected 3, got 4.'):
            data_table.set_column(col_key, pd.Series([1, 2, 3, 4]))

    def test_exist_name_error(self):
        # Test if ExistsNameError is raised for duplicated column types
        df1 = pd.DataFrame({'col0': [1, 2, 3]})
        df2 = pd.DataFrame({'col0': ['a', 'b', 'c']})
        df = pd.concat([df1, df2], axis=1)
        with pytest.raises(KeyError, match='Name "col0" already exists.'):
            DataTable(df)

    # To fix bug 479734
    def test_set_column_if_feature(self, data_table):
        data_table.meta_data.score_column_names = {'score_type1': 'col1'}
        assert not data_table.meta_data.column_attributes['col1'].is_feature
        column = pd.Series(['a', 'b', 'c'])
        data_table.set_column('col1', column)
        assert not data_table.meta_data.column_attributes['col1'].is_feature

    def test_create_data_table_with_mixed_type_column(self):
        df = pd.DataFrame({'col0': ['a', 1, True, pd.Timestamp(2017, 1, 1, 12), None, np.nan, pd.NaT,
                                    pd.Timedelta('1 days')]})
        dt = DataTable(df)
        assert dt

    def test_speed(self):
        row_number = int(1e6)
        df = pd.DataFrame(columns=['col0'], index=list(range(row_number)))
        df.iloc[:, 0] = list(range(row_number))
        df.iloc[0, 0] = None
        with TimeProfile('Create DataTable with missing value'):
            dt = DataTable(df)

        assert is_float_dtype(dt.data_frame['col0'].dtype)


def test_from_dfd(data_frame, tmp_path):
    # Drop col6 since it will introduce bug when calling df.describe in DataFrameVisualizer if df has time span column.
    # Todo: Fix bug when the df has time span columns.
    data_frame = data_frame.drop(columns=['col6'])
    data_table = DataTable(data_frame)
    save_data_frame_to_directory(tmp_path, data=data_table.data_frame, schema=data_table.meta_data.to_dict())
    dfd = load_data_frame_from_directory(tmp_path)
    new_dt = DataTable.from_dfd(dfd)
    assert data_table.data_frame.equals(new_dt.data_frame)

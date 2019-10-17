import pytest
import pandas as pd
import numpy as np

from azureml.studio.common.error import DuplicatedColumnNameError
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.modules.datatransform.manipulation.select_columns.select_columns import SelectColumnsModule


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
def data_table(data_frame):
    return DataTable(data_frame)


@pytest.fixture
def column_selection_col01():
    return DataTableColumnSelectionBuilder().include_col_names('col0', 'col1').build()


def test_run(data_frame, data_table, column_selection_col01):

    data_table_selected = SelectColumnsModule.run(
        table=data_table,
        feature_list=column_selection_col01)[0]
    data_frame_selected = data_frame.iloc[:, [0, 1]]
    assert data_table_selected.data_frame.equals(data_frame_selected)
    assert data_table_selected.meta_data.column_attributes\
        == DataFrameSchema.generate_column_attributes(data_frame_selected)

    # Assert meta data is shallow copied
    assert data_table.meta_data.column_attributes[0] is data_table_selected.meta_data.column_attributes[0]


@pytest.fixture
def column_selection_duplicated_cols():
    return DataTableColumnSelectionBuilder().keep_order_and_duplicates(True)\
        .include_col_names('col2', 'col3', 'col3', 'col1', 'col1').build()


def test_duplicated_columns(data_table, column_selection_duplicated_cols):
    err_msg = 'The name "col3" is duplicated. Details: Duplicated columns are selected.'
    with pytest.raises(DuplicatedColumnNameError, match=err_msg):
        SelectColumnsModule.run(
            table=data_table,
            feature_list=column_selection_duplicated_cols,
        )

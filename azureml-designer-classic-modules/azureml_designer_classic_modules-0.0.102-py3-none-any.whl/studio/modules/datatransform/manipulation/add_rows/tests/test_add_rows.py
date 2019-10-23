import pandas as pd

import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.data_frame_schema import FeatureChannel
from azureml.studio.common.error import NotEqualColumnNamesError, ColumnCountNotEqualError
from azureml.studio.modules.datatransform.manipulation.add_rows.add_rows import AddRowsModule


@pytest.fixture
def input_data_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B", "C"],
            data=[
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [9, 10, 11]
            ]))


@pytest.fixture
def input_data_table_2():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B", "C"],
            data=[
                [10, 11, 12],
                [13, 14, 15]
            ]))


@pytest.fixture
def input_data_table_3():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B", "D"],
            data=[
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [9, 10, 11]
            ]))


@pytest.fixture
def input_data_table_4():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))


def feature_channels(col_name):
    feature_channel = FeatureChannel(name='Binary Classification Scores',
                                     is_normalized=True, feature_column_names=[col_name])
    return {'Binary Classification Scores': feature_channel}


def test_add_rows(input_data_table_1, input_data_table_2):
    result = AddRowsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.number_of_rows == input_data_table_1.number_of_rows + input_data_table_2.number_of_rows


def test_add_columns_with_meta_data(input_data_table_1, input_data_table_2):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "A"}
    input_data_table_2.meta_data.score_column_names = {'score_type2': "C"}

    input_data_table_1.meta_data.label_column_name = "B"
    input_data_table_1.meta_data.feature_channels.update(feature_channels("A"))

    result = AddRowsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.number_of_rows == input_data_table_1.number_of_rows + input_data_table_2.number_of_rows
    assert result.meta_data.score_column_names == {**input_data_table_1.meta_data.score_column_names,
                                                   **input_data_table_2.meta_data.score_column_names}
    assert result.meta_data.label_column_name == input_data_table_1.meta_data.label_column_name
    assert result.meta_data.feature_channels == input_data_table_1.meta_data.feature_channels


def test_add_columns_with_conflicted_meta_data(input_data_table_1, input_data_table_2):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "A"}
    input_data_table_2.meta_data.score_column_names = {'score_type1': "C"}

    input_data_table_1.meta_data.label_column_name = "B"

    input_data_table_1.meta_data.feature_channels.update(feature_channels("A"))
    input_data_table_2.meta_data.feature_channels.update(feature_channels("C"))

    result = AddRowsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.number_of_rows == input_data_table_1.number_of_rows + input_data_table_2.number_of_rows
    assert result.meta_data.score_column_names == {'score_type1': "A"}
    assert result.meta_data.label_column_name == input_data_table_1.meta_data.label_column_name
    assert result.meta_data.feature_channels == input_data_table_1.meta_data.feature_channels


def test_add_columns_conflicted_column_name(input_data_table_1, input_data_table_3):
    with pytest.raises(NotEqualColumnNamesError, match="Column names are not the same for column 2"):
        AddRowsModule.run(
            table1=input_data_table_1,
            table2=input_data_table_3
        )


def test_add_columns_conflicted_column_count(input_data_table_1, input_data_table_4):
    with pytest.raises(ColumnCountNotEqualError):
        AddRowsModule.run(
            table1=input_data_table_1,
            table2=input_data_table_4
        )

import pandas as pd

import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.data_frame_schema import FeatureChannel
from azureml.studio.modules.datatransform.manipulation.add_columns.add_columns import AddColumnsModule


@pytest.fixture
def input_data_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))


@pytest.fixture
def input_data_table_2():
    return DataTable(
        pd.DataFrame(
            columns=["C", "D", "E"],
            data=[
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [9, 10, 11]
            ]))


@pytest.fixture
def input_data_table_3():
    return DataTable(
        pd.DataFrame(
            columns=["B", "C"],
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


def test_add_columns(input_data_table_1, input_data_table_2):

    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.column_names == input_data_table_1.column_names + input_data_table_2.column_names


def test_add_columns_conflicted_column_name(input_data_table_1, input_data_table_3):
    table_1_column_names = input_data_table_1.column_names
    table_3_column_names = input_data_table_3.column_names
    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_3
    )[0]

    assert result.column_names == ["A", "B_1", "B_2", "C"]
    assert table_1_column_names == input_data_table_1.column_names
    assert table_3_column_names == input_data_table_3.column_names


def test_add_columns_with_meta_data(input_data_table_1, input_data_table_2):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "A"}
    input_data_table_2.meta_data.score_column_names = {'score_type2': "C"}

    input_data_table_1.meta_data.label_column_name = "B"
    input_data_table_1.meta_data.feature_channels.update(feature_channels("A"))

    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.column_names == input_data_table_1.column_names + input_data_table_2.column_names
    assert result.meta_data.score_column_names == {**input_data_table_1.meta_data.score_column_names,
                                                   **input_data_table_2.meta_data.score_column_names}
    assert result.meta_data.label_column_name == input_data_table_1.meta_data.label_column_name
    assert result.meta_data.feature_channels == input_data_table_1.meta_data.feature_channels


def test_add_columns_with_conflicted_meta_data(input_data_table_1, input_data_table_2):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "A"}
    input_data_table_2.meta_data.score_column_names = {'score_type1': "C", 'score_type2': "D"}

    input_data_table_1.meta_data.label_column_name = "B"
    input_data_table_2.meta_data.label_column_name = "E"

    input_data_table_1.meta_data.feature_channels.update(feature_channels("A"))
    input_data_table_2.meta_data.feature_channels.update(feature_channels("C"))

    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_2
    )[0]

    assert result.column_names == input_data_table_1.column_names + input_data_table_2.column_names
    assert result.meta_data.score_column_names == {'score_type1': "A", 'score_type2': "D"}
    assert result.meta_data.label_column_name == input_data_table_1.meta_data.label_column_name
    assert result.meta_data.feature_channels == input_data_table_1.meta_data.feature_channels


def test_add_columns_with_conflicted_column_and_meta_data_score(input_data_table_1, input_data_table_3):
    input_data_table_1.meta_data.score_column_names = {'score_type1': "B"}
    input_data_table_3.meta_data.score_column_names = {'score_type2': "B"}
    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_3
    )[0]

    assert result.column_names == ["A", "B_1", "B_2", "C"]
    assert result.meta_data.score_column_names == {'score_type1': "B_1", 'score_type2': "B_2"}


def test_add_columns_with_conflicted_column_and_meta_data_label(input_data_table_1, input_data_table_3):
    input_data_table_1.meta_data.label_column_name = "B"
    input_data_table_3.meta_data.label_column_name = "B"

    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_3
    )[0]

    assert result.column_names == ["A", "B_1", "B_2", "C"]
    assert result.meta_data.label_column_name == "B_1"


def test_add_columns_with_conflicted_column_and_meta_data_feature_channel(input_data_table_1, input_data_table_3):
    input_data_table_1.meta_data.feature_channels.update(feature_channels("B"))
    input_data_table_3.meta_data.feature_channels.update(feature_channels("B"))

    result = AddColumnsModule.run(
        table1=input_data_table_1,
        table2=input_data_table_3
    )[0]

    assert result.column_names == ["A", "B_1", "B_2", "C"]
    assert result.meta_data.feature_channels == feature_channels("B_1")

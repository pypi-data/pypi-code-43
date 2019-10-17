import pandas as pd
import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import TooFewColumnsInDatasetError
from azureml.studio.modules.datatransform.manipulation.select_columns_transform.select_columns_transform import \
    SelectColumnsTransformModule, SelectColumnsTransform


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
            columns=["B", "C", "D"],
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


@pytest.fixture
def input_data_table_4():
    return DataTable(
        pd.DataFrame(
            columns=["D", "E"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))


def test_select_columns_transform(input_data_table_1, input_data_table_2, input_data_table_3):
    # Transformed columns: A, B, C
    transform = SelectColumnsTransformModule.run(table=input_data_table_1)[0]

    # Input columns: A, B, C
    # Expected output columns: A, B, C
    output_data_table_1 = transform.apply(input_data_table_1)
    assert output_data_table_1.column_names == input_data_table_1.column_names
    assert output_data_table_1.number_of_rows == input_data_table_1.number_of_rows

    # Input columns: B, C, D
    # Expected output columns: B, C
    output_data_table_2 = transform.apply(input_data_table_2)
    assert output_data_table_2.column_names == input_data_table_3.column_names
    assert output_data_table_2.number_of_rows == input_data_table_3.number_of_rows

    # Input columns: B, C
    # Expected output columns: B, C
    output_data_table_3 = transform.apply(input_data_table_3)
    assert output_data_table_3.column_names == input_data_table_3.column_names
    assert output_data_table_3.number_of_rows == input_data_table_3.number_of_rows


def test_select_columns_transform_with_score_names(input_data_table_1, input_data_table_2, input_data_table_3):
    # Transformed columns: A, B, C
    transform = SelectColumnsTransformModule.run(table=input_data_table_1)[0]

    # Input columns: B, C, D
    # Scored columns: D
    # Expected output columns: B, C, D
    input_data_table_2.meta_data.score_column_names = {"Score_Type_1": "D"}
    output_data_table_1 = transform.apply(input_data_table_2)
    assert output_data_table_1.column_names == input_data_table_2.column_names
    assert output_data_table_1.number_of_rows == input_data_table_2.number_of_rows

    # Input columns: B, C, D
    # Scored columns: C
    # Expected output columns: B, C
    input_data_table_2.meta_data.score_column_names = {"Score_Type_1": "C"}
    output_data_table_2 = transform.apply(input_data_table_2)
    assert output_data_table_2.column_names == input_data_table_3.column_names
    assert output_data_table_2.number_of_rows == input_data_table_3.number_of_rows


def test_select_columns_transform_with_label(input_data_table_1, input_data_table_2, input_data_table_3):
    # Transformed columns: A, B, C
    transform = SelectColumnsTransformModule.run(table=input_data_table_1)[0]

    # Input columns: B, C, D
    # Label columns: D
    # Expected output columns: B, C, D
    input_data_table_2.meta_data.label_column_name = "D"
    output_data_table_1 = transform.apply(input_data_table_2)
    assert output_data_table_1.column_names == input_data_table_2.column_names
    assert output_data_table_1.number_of_rows == input_data_table_2.number_of_rows

    # Input columns: B, C, D
    # Label columns: C
    # Expected output columns: B, C
    input_data_table_2.meta_data.label_column_name = "C"
    output_data_table_2 = transform.apply(input_data_table_2)
    assert output_data_table_2.column_names == input_data_table_3.column_names
    assert output_data_table_2.number_of_rows == input_data_table_3.number_of_rows


def test_select_columns_transform_against_unmatched_data_table(input_data_table_1, input_data_table_4):
    # Transformed columns: A, B, C
    transform = SelectColumnsTransformModule.run(table=input_data_table_1)[0]

    # Input columns: D, E
    # Expected output columns: <empty>
    output_data_table_1 = transform.apply(input_data_table_4)
    assert output_data_table_1.number_of_columns == 0


def test_select_columns_transform_empty_input_data_table():
    with pytest.raises(TooFewColumnsInDatasetError,
                       match='Number of columns in input dataset "Dataset with desired columns" '):
        SelectColumnsTransformModule.run(table=DataTable())

    transform = SelectColumnsTransform(["dummy_column"])
    with pytest.raises(TooFewColumnsInDatasetError,
                       match='Number of columns in input dataset "Dataset" '):
        transform.apply(dt=DataTable())

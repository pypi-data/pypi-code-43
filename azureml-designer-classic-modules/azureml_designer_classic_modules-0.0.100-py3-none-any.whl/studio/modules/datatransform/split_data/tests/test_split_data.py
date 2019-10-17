import numpy as np
import pandas as pd
import pytest

from azureml.studio.common.datatable.data_table import DataTable, DataTableColumnSelectionBuilder as CSB
from azureml.studio.core.utils.column_selection import ColumnKind
from azureml.studio.modules.datatransform.split_data.split_data import SplitterSplitMode, SplitDataModule, \
    SplitterTrueFalseType
from azureml.studio.common.error import ColumnNotFoundError, ParameterParsingError, InvalidColumnTypeError, \
    NoColumnsSelectedError


@pytest.fixture
def input_data_table():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ],
            index=list("xyzw")
        ))


@pytest.fixture
def input_data_table2():
    df = pd.DataFrame(
        columns=["A", "B"],
        data=[
            ["a", 1],
            ["ab", 2],
            ["abc", 3],
            ["c", 4],
            ["d", np.nan]
        ])
    return DataTable(df)


@pytest.fixture
def input_data_table3():
    df = pd.DataFrame(
        columns=["A", "B"],
        data=[
            [1, 11],
            [1, 12],
            [2, 13],
            [2, 14],
            [3, 15],
            [3, 16],
            [4, 17],
            [4, 18],
        ])
    return DataTable(df)


@pytest.fixture
def input_data_table_category():
    df = pd.DataFrame(
        columns=["A", "B"],
        data=[
            [1, 11],
            [1, 12],
            [2, 13],
            [2, 14],
            [3, 15],
            [3, 16],
            [4, 17],
            [4, 18],
        ])
    df["B"] = df["B"].astype("category")
    return DataTable(df)


@pytest.fixture
def column_selection_a():
    return CSB().include_col_names("A").build()


def test_non_random_split(input_data_table):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table,
        mode=SplitterSplitMode.GenericSplit,
        ratio=0.5,
        random_flag=False,
        seed=0,
        stratify_flag=SplitterTrueFalseType.FALSE
    )
    assert dt1.number_of_rows == input_data_table.number_of_rows * 0.5
    assert dt1.number_of_rows == dt2.number_of_rows
    assert np.array_equal(dt1.data_frame.iloc[0].values, [0, 1])


def test_random_split(input_data_table):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table,
        mode=SplitterSplitMode.GenericSplit,
        ratio=0.5,
        random_flag=True,
        seed=0,
        stratify_flag=SplitterTrueFalseType.FALSE
    )
    assert dt1.number_of_rows == input_data_table.number_of_rows * 0.5
    assert dt1.number_of_rows == dt2.number_of_rows


def test_split_stratify(input_data_table3, column_selection_a):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table3,
        mode=SplitterSplitMode.GenericSplit,
        ratio=0.5,
        random_flag=False,
        seed=0,
        stratify_flag=SplitterTrueFalseType.TRUE,
        strats_column=column_selection_a
    )
    assert dt1.number_of_rows == input_data_table3.number_of_rows * 0.5
    assert dt1.number_of_rows == dt2.number_of_rows
    assert np.array_equal(dt1.data_frame['B'], [11, 13, 15, 17])
    assert np.array_equal(dt2.data_frame['B'].values, [12, 14, 16, 18])


def test_split_stratify_rand(input_data_table3, column_selection_a):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table3,
        mode=SplitterSplitMode.GenericSplit,
        ratio=0.5,
        random_flag=True,
        seed=0,
        stratify_flag=SplitterTrueFalseType.TRUE,
        strats_column=column_selection_a
    )
    assert dt1.number_of_rows == input_data_table3.number_of_rows * 0.5
    assert dt1.number_of_rows == dt2.number_of_rows
    assert set(dt1.data_frame['A']) == set([1, 2, 3, 4])
    assert set(dt2.data_frame['A']) == set([1, 2, 3, 4])


def test_split_reg_ex_1(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RegEx,
        reg_ex=r'(\1) ^ab'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 2


def test_split_reg_ex_2(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RegEx,
        reg_ex=r'\"A" ^ab'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 2


def test_split_reg_ex_3(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RegEx,
        reg_ex=r'\"A" b'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 2


# 416207
def test_split_reg_ex_4(input_data_table_category):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table_category,
        mode=SplitterSplitMode.RegEx,
        reg_ex=r'\"B" 1[1-4]'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table_category.number_of_rows
    assert dt1.number_of_rows == 4


def test_split_rel_ex_1(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RelEx,
        rel_ex=r'(\2) >2'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 2


def test_split_rel_ex_2(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RelEx,
        rel_ex=r'\"B" !=0'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 4


def test_split_rel_ex_3(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RelEx,
        rel_ex=r'\"B" >=2 & <=3'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 2


def test_split_rel_ex_4(input_data_table2):
    # pylint: disable=no-value-for-parameter
    dt1, dt2 = SplitDataModule.run(
        table=input_data_table2,
        mode=SplitterSplitMode.RelEx,
        rel_ex=r'\"A" ==a'
    )
    assert dt1.number_of_rows + dt2.number_of_rows == input_data_table2.number_of_rows
    assert dt1.number_of_rows == 1


def test_error_split_reg_ex_1(input_data_table2):
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RegEx,
            reg_ex=r'xx yy'
        )


def test_error_split_reg_ex_2(input_data_table2):
    with pytest.raises(ColumnNotFoundError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RegEx,
            reg_ex=r'\"X" b'
        )


def test_error_split_reg_ex_3(input_data_table2):
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RegEx,
            reg_ex=r'\"B" ('
        )


def test_error_split_rel_ex_1(input_data_table2):
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'X !=0'
        )


def test_error_split_rel_ex_2(input_data_table2):
    with pytest.raises(ColumnNotFoundError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"X" !=0'
        )


def test_error_split_rel_ex_3(input_data_table2):
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"B" yyy'
        )


def test_error_split_rel_ex_4(input_data_table2):
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"B" !=b_b'
        )


def test_error_split_rel_ex_5(input_data_table2):
    # string column does not support < <= > >=
    with pytest.raises(InvalidColumnTypeError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"A" <n'
        )


def test_error_split_rel_ex_6(input_data_table2):
    # invalid operator
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"A" ~n'
        )


def test_error_split_rel_ex_7(input_data_table2):
    # double and/or operator
    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.RelEx,
            rel_ex=r'\"A" ==1&&==2'
        )


def test_bug_509163(input_data_table2):
    strats_column = CSB().include_col_kinds(ColumnKind.LABEL).build()

    with pytest.raises(NoColumnsSelectedError):
        # pylint: disable=no-value-for-parameter
        SplitDataModule.run(
            table=input_data_table2,
            mode=SplitterSplitMode.GenericSplit,
            ratio=0.8,
            random_flag=True,
            seed=0,
            stratify_flag=SplitterTrueFalseType.TRUE,
            strats_column=strats_column
        )

import itertools
import numpy as np
import pandas as pd
import pytest
import re

from azureml.studio.core.utils.column_selection import ColumnType
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder as CSB
from azureml.studio.common.error import TooFewColumnsInDatasetError, NoColumnsSelectedError, DuplicatedColumnNameError,\
    InconsistentSizeError, JoinOnIncompatibleColumnTypesError
from azureml.studio.modules.datatransform.manipulation.join_data.join_data import JoinDataModule, JoinType


@pytest.fixture()
def input_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B", "C"],
            data=[
                [1, 1, "one"],
                [2, 2, "two"],
                [3, 2, "two"],
                [4, 3, "three"],
                [5, 3, "three"],
                [6, 4, "four"],
                [7, 6, "six"],
                [8, None, None],
            ]))


@pytest.fixture()
def input_table_2():
    return DataTable(
        pd.DataFrame(
            columns=["A", "C", "B", "D"],
            data=[
                [1, "one", 1, "One"],
                [2, "two", 2, "Two"],
                [3, "three", 3, "Three"],
                [4, "three", 3, "Three"],
                [5, "four", 4, "Four"],
                [6, "four", 4, "Four"],
                [7, "five", 5, "Five"],
                [8, None, None, None],
            ]))


@pytest.fixture()
def keys1():
    return CSB().include_col_names('B').build()


@pytest.fixture()
def keys2():
    return CSB().include_col_names('B').build()


@pytest.fixture()
def multi_keys1():
    return CSB().keep_order_and_duplicates(True).include_col_names('C', 'B').build()


@pytest.fixture()
def multi_keys2():
    return CSB().keep_order_and_duplicates(True).include_col_names('C', 'B').build()


@pytest.fixture()
def input_large_table_1(row_count):
    df = pd.DataFrame(data={
        "A": np.arange(0, row_count),
        "B": np.arange(0, row_count),
    })
    return DataTable(df)


@pytest.fixture()
def input_large_table_2(row_count):
    df = pd.DataFrame(data={
        "A": np.arange(0, row_count),
        "B": np.arange(0, row_count) + int(row_count/2),
    })
    df.append(pd.Series(), ignore_index=True)
    return DataTable(df)


def exp_table_inner_join():
    return pd.DataFrame(
        columns=["A", "A_R"],
        data=[
            [1, 1],
            [2, 2],
            [3, 2],
            [4, 3],
            [4, 4],
            [5, 3],
            [5, 4],
            [6, 5],
            [6, 6],
        ]
    )


def exp_table_left_join():
    return pd.DataFrame(
        columns=["A", "A_R"],
        data=[
            [1, 1],
            [2, 2],
            [3, 2],
            [4, 3],
            [4, 4],
            [5, 3],
            [5, 4],
            [6, 5],
            [6, 6],
            [7, None],
            [8, None],
        ]
    )


def exp_table_full_join():
    return pd.DataFrame(
        columns=["A", "A_R"],
        data=[
            [1, 1],
            [2, 2],
            [3, 2],
            [4, 3],
            [4, 4],
            [5, 3],
            [5, 4],
            [6, 5],
            [6, 6],
            [7, None],
            [8, None],
            [None, 7],
            [None, 8]
        ]
    )


def exp_table_semi_join():
    return pd.DataFrame(
        columns=["A"],
        data=[
            [1],
            [2],
            [3],
            [4],
            [5],
            [6],
        ]
    )


def check_if_data_frame_equal(df, df_exp):
    df = df[list(df_exp.columns)]
    assert df.equals(df_exp)


def check_output_columns(dt1, dt2, key1, key2, join_type, dtout, keep2):
    if join_type == JoinType.LeftSemi:
        assert dt1.column_names == dtout.column_names
    elif keep2:
        exp_columns = dt1.column_names + [n+"_R" if n in dt1.column_names else n for n in dt2.column_names]
        assert exp_columns == dtout.column_names
    else:
        key2_indices = key2.select_column_indexes(dt2)
        merged_df2_columns = [n for i, n in zip(range(dt2.number_of_columns), dt2.column_names)
                              if i not in key2_indices]
        exp_columns = dt1.column_names + [n+"_R" if n in dt1.column_names else n for n in merged_df2_columns]
        assert exp_columns == dtout.column_names


@pytest.mark.parametrize('join_type, df_exp', [
    (JoinType.Inner, exp_table_inner_join()),
    (JoinType.LeftOuter, exp_table_left_join()),
    (JoinType.FullOuter, exp_table_full_join()),
    (JoinType.LeftSemi, exp_table_semi_join())
])
def test_basic_join(input_table_1, input_table_2, keys1, keys2, join_type, df_exp):
    keep2 = True
    dt = JoinDataModule.run(
        table1=input_table_1.clone(),
        table2=input_table_2.clone(),
        keys1=keys1,
        keys2=keys2,
        case_sensitive=False,
        join_type=join_type,
        keep2=keep2
    )[0]
    check_if_data_frame_equal(dt.data_frame, df_exp)
    check_output_columns(input_table_1, input_table_2, keys1, keys2, join_type, dt, keep2)


def join_multi_key_params():
    return [
        (x[0], x[1], y, z) for x, y, z in itertools.product(
            [
                (JoinType.Inner, exp_table_inner_join()),
                (JoinType.LeftOuter, exp_table_left_join()),
                (JoinType.FullOuter, exp_table_full_join()),
                (JoinType.LeftSemi, exp_table_semi_join())
            ],
            [True, False],
            [True, False]
        )
    ]


@pytest.mark.parametrize('join_type, df_exp, case_sensitive, keep2', join_multi_key_params())
def test_join_multi_key(input_table_1, input_table_2, multi_keys1, multi_keys2, join_type, df_exp,
                        case_sensitive, keep2):
    dt = JoinDataModule.run(
        table1=input_table_1.clone(),
        table2=input_table_2.clone(),
        keys1=multi_keys1,
        keys2=multi_keys2,
        case_sensitive=False,
        join_type=join_type,
        keep2=keep2
    )[0]
    check_if_data_frame_equal(dt.data_frame, df_exp)
    check_output_columns(input_table_1, input_table_2, multi_keys1, multi_keys2, join_type, dt, keep2)


@pytest.mark.parametrize('join_type, row_count, case_sensitive, keep2', itertools.product(
    [JoinType.Inner, JoinType.LeftOuter, JoinType.FullOuter, JoinType.LeftSemi],
    [10000, 100000, 1000000],
    [True, False],
    [True, False]
))
def test_join_performance(input_large_table_1, input_large_table_2, keys1, keys2, join_type, row_count,
                          case_sensitive, keep2):
    dt = JoinDataModule.run(
        table1=input_large_table_1,
        table2=input_large_table_2,
        keys1=keys1,
        keys2=keys2,
        case_sensitive=case_sensitive,
        join_type=join_type,
        keep2=keep2
    )[0]

    exp_row_count = {
        JoinType.Inner: int(row_count / 2),
        JoinType.LeftOuter: row_count,
        JoinType.FullOuter: int(row_count * 1.5),
        JoinType.LeftSemi: int(row_count / 2),
    }

    assert dt.number_of_rows == exp_row_count[join_type]


@pytest.mark.parametrize('join_type', [JoinType.Inner, JoinType.LeftOuter, JoinType.FullOuter, JoinType.LeftSemi])
def test_join_category(keys1, keys2, join_type):
    dt1 = DataTable(pd.DataFrame(
        data={"B": ["x3", 1, 5, 2.0]},
        dtype="category"
    ))
    dt2 = DataTable(pd.DataFrame(
        data={"B": ["5", "X3", 2]},
        dtype="category"
    ))
    dt_out = JoinDataModule.run(
        table1=dt1,
        table2=dt2,
        keys1=keys1,
        keys2=keys2,
        case_sensitive=False,
        join_type=join_type,
        keep2=True
    )[0]

    exp_row_count = {
        JoinType.Inner: 2,
        JoinType.LeftOuter: 4,
        JoinType.FullOuter: 5,
        JoinType.LeftSemi: 2,
    }

    assert dt_out.number_of_rows == exp_row_count[join_type]


@pytest.mark.parametrize('columns1, columns2, key1_names, key2_names, expect_columns', [
    (['A', 'B'], ['A', 'B'], ['A'], ['A'], ['A', 'B', 'A_R', 'B_R']),
    (['A', 'B'], ['A', 'B'], ['B'], ['B'], ['A', 'B', 'A_R', 'B_R']),
    (['A', 'B_R'], ['A', 'B'], ['A'], ['A'], ['A', 'B_R', 'A_R1', 'B']),
    (['A', 'B', 'B_R'], ['A', 'B', 'B_R1'], ['A'], ['A'], ['A', 'B', 'B_R', 'A_R2', 'B_R2', 'B_R1']),
    (['A', 'B', 'B_R', 'B_R1', 'B_R2'], ['A', 'B', 'B_R1'], ['A'], ['A'],
     ['A', 'B', 'B_R', 'B_R1', 'B_R2', 'A_R3', 'B_R3', 'B_R1_R3']),
    (['A', 'B'], ['A', 'B'], ['B'], ['A'], ['A', 'B', 'A_R', 'B_R']),
    (['A', 'B', 'C'], ['A', 'B', 'D'], ['A', 'B'], ['A', 'B'], ['A', 'B', 'C', 'A_R', 'B_R', 'D']),
    (['A', 'B', 'C', 'D'], ['C', 'D', 'E', 'F'], ['C', 'D'], ['D', 'E'], ['A', 'B', 'C', 'D', 'C_R', 'D_R', 'E', 'F']),
])
def test_rename_on_join(columns1, columns2, key1_names, key2_names, expect_columns):
    dt1 = DataTable(pd.DataFrame(
        data=[np.repeat(1, len(columns1))],
        columns=columns1
    ))
    dt2 = DataTable(pd.DataFrame(
        data=[np.repeat(1, len(columns2))],
        columns=columns2
    ))
    dt_out = JoinDataModule.run(
        table1=dt1,
        table2=dt2,
        keys1=CSB().keep_order_and_duplicates(True).include_col_names(*key1_names).build(),
        keys2=CSB().keep_order_and_duplicates(True).include_col_names(*key2_names).build(),
        case_sensitive=False,
        join_type=JoinType.FullOuter,
        keep2=True
    )[0]

    assert dt_out.column_names == expect_columns


def test_param_validate_errors():
    with pytest.raises(TooFewColumnsInDatasetError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": []})),
            table2=DataTable(),
            keys1=CSB().include_col_names('A').build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(TooFewColumnsInDatasetError):
        JoinDataModule.run(
            table1=DataTable(),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().include_col_names('A').build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(NoColumnsSelectedError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": []})),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().include_col_types(ColumnType.NUMERIC).build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(NoColumnsSelectedError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": []})),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().include_col_names('A').build(),
            keys2=CSB().include_col_types(ColumnType.NUMERIC).build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(DuplicatedColumnNameError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": []})),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().keep_order_and_duplicates(True).include_col_names('A', 'A').build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(DuplicatedColumnNameError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": []})),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().include_col_names('A').build(),
            keys2=CSB().keep_order_and_duplicates(True).include_col_names('A', 'A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )

    with pytest.raises(InconsistentSizeError):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": [], "B": []})),
            table2=DataTable(pd.DataFrame(data={"A": []})),
            keys1=CSB().include_col_names('A', 'B').build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.Inner,
            keep2=True
        )


def test_merge_incompatible_column_type_errors():
    with pytest.raises(JoinOnIncompatibleColumnTypesError, match=re.escape(
            r"Key column element types are not compatible.(left: A:object; right: A:float64)")):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": ["x", "y"]})),
            table2=DataTable(pd.DataFrame(data={"A": [1, None]})),
            keys1=CSB().include_col_names('A').build(),
            keys2=CSB().include_col_names('A').build(),
            case_sensitive=False,
            join_type=JoinType.FullOuter,
            keep2=True
        )

    with pytest.raises(JoinOnIncompatibleColumnTypesError, match=re.escape(
            r"Key column element types are not compatible.(left: A:object, B:int64; right: A:float64, B:int64)")):
        JoinDataModule.run(
            table1=DataTable(pd.DataFrame(data={"A": ["x", "y"], "B": [3, 5]})),
            table2=DataTable(pd.DataFrame(data={"A": [1, None], "B": [3, 5]})),
            keys1=CSB().include_col_names('A', 'B').build(),
            keys2=CSB().include_col_names('A', 'B').build(),
            case_sensitive=False,
            join_type=JoinType.FullOuter,
            keep2=True
        )

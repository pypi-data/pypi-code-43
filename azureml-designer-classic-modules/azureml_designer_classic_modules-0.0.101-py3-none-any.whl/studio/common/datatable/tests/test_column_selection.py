import pandas as pd
import numpy as np

import pytest

from azureml.studio.core.utils.column_selection import ColumnType, ColumnKind
from azureml.studio.common.datatable.data_table import DataTableColumnSelection, DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import NoColumnsSelectedError, ColumnNotFoundError, ColumnIndexParsingError, \
    InvalidColumnIndexRangeError
from azureml.studio.common.datatable.constants import ElementTypeName, ColumnTypeName


@pytest.fixture
def simple_data_table():
    return DataTable(pd.DataFrame({'float': [1.0],
                                   'int': [1],
                                   'datetime': [pd.Timestamp('20180310')],
                                   'string': ['foo']}))


def complex_data_table():
    df = pd.DataFrame()
    df['int'] = [2, 1, 10]
    df['float'] = [np.nan, 1.6, 1]
    df['str'] = [np.nan, 'a', 'b']
    df['bool'] = [None, True, False]
    df['category'] = pd.Series([np.nan, 'c', 'f']).astype('category')
    df['datetime'] = pd.to_datetime(
        arg=pd.Series([np.nan, '20190129', np.nan]), format='%Y%m%d', errors='coerce')
    df['timedelta'] = pd.to_timedelta(
        arg=pd.Series([np.nan, 30, 'c']), unit='d', errors='coerce')
    return DataTable(df)


def test_rule_type_all_columns(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false}],"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names
    assert len(selected_data_table.meta_data.column_attributes) == len(simple_data_table.meta_data.column_attributes)
    assert selected_data_table.meta_data.column_attributes[0] == simple_data_table.meta_data.column_attributes[0]


def test_rule_type_all_columns_with_include(simple_data_table):
    include_column_names = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false},'
        '{"ruleType":"ColumnNames","columns":["float","int"],"exclude":false}],"ui":{"withRules":true}}')
    selected_data_table = include_column_names.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names


def test_rule_type_all_columns_with_exclude(simple_data_table):
    exclude_column_names = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false},'
        '{"ruleType":"ColumnNames","columns":["float","int"],"exclude":true}],"ui":{"withRules":true}}')
    selected_data_table = exclude_column_names.select(simple_data_table)
    assert selected_data_table.column_names == ['datetime', 'string']

    exclude_all_features = DataTableColumnSelectionBuilder().include_all().exclude_col_kinds(ColumnKind.FEATURE).build()
    selected_data_table = exclude_all_features.select(simple_data_table)
    assert selected_data_table.column_names == []

    simple_data_table.meta_data.label_column_name = "string"
    exclude_all_labels = DataTableColumnSelectionBuilder().include_all().exclude_col_kinds(ColumnKind.LABEL).build()
    selected_data_table = exclude_all_labels.select(simple_data_table)
    assert "string" not in selected_data_table.column_names

    simple_data_table.meta_data.score_column_names = {"AAA": "int", "BBB": "float"}
    exclude_all_scores = DataTableColumnSelectionBuilder().include_all().exclude_col_kinds(ColumnKind.SCORE).build()
    selected_data_table = exclude_all_scores.select(simple_data_table)
    assert set(selected_data_table.column_names) == set(["datetime", "string"])


def test_rule_type_column_name(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["float","int"],"exclude":false}]}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_rule_type_column_indexes(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["1","2"],"exclude":false}],'
        '"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_rule_type_column_indexes_range(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["1-3"],"exclude":false}],'
        '"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int', 'datetime']


def test_rule_type_column_types(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Numeric"],'
        '"columnKinds":["All"]}],"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_rule_type_column_types_with_exclude(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_all().exclude_col_types(ColumnTypeName.STRING).build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int', 'datetime']


# Fix bug 457604: In module "select columns",  "exclude column type" does not work
@pytest.mark.parametrize(
    'exclude_column_type, exclude_column_names',
    [
        (ColumnType.STRING, ['str']),
        (ColumnType.INTEGER, ['int']),
        (ColumnType.DOUBLE, ['float']),
        (ColumnType.BOOLEAN, ['bool']),
        (ColumnType.DATETIME, ['datetime']),
        (ColumnType.TIME_SPAN, ['timedelta']),
        (ColumnType.CATEGORICAL, ['category']),
        (ColumnType.NUMERIC, ['int', 'float'])
    ]
)
def test_rule_type_column_types_with_exclude_complex_data_table(exclude_column_type, exclude_column_names):
    csb = DataTableColumnSelectionBuilder()
    dt = complex_data_table()
    column_selection = csb.include_all().exclude_col_types(exclude_column_type).build()
    dt_selected = column_selection.select(dt)
    assert set(dt_selected.column_names) == set(dt.column_names) - set(exclude_column_names)


def test_rule_type_column_types_with_categorical(simple_data_table):
    simple_data_table.set_column_element_type(3, ElementTypeName.CATEGORY)

    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Categorical"],'
        '"columnKinds":["All"]}],"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['string']


def test_rule_type_column_types_with_kinds(simple_data_table):
    include_all = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.ALL).build()
    selected_data_table = include_all.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names

    include_all_features = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.FEATURE).build()
    selected_data_table = include_all_features.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names

    simple_data_table.meta_data.label_column_name = "string"
    include_all_labels = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.LABEL).build()
    selected_data_table = include_all_labels.select(simple_data_table)
    assert selected_data_table.column_names == ["string"]

    simple_data_table.meta_data.score_column_names = {"AAA": "int", "BBB": "float"}
    include_all_scores = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.SCORE).build()
    selected_data_table = include_all_scores.select(simple_data_table)
    assert set(selected_data_table.column_names) == set(["int", "float"])


def test_rule_type_no_columns_include_and_exclude(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Numeric"],'
        '"columnKinds":["All"]},{"ruleType":"ColumnNames","columns":["float"],"exclude":true}],'
        '"ui":{"withRules":true}}')
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['int']


def test_exception_no_columns_selected():
    with pytest.raises(NoColumnsSelectedError):
        DataTableColumnSelection(
            '{"isFilter":true,"rules":[],"ui":{"withRules":true}}')


def test_exception_column_not_found_in_name_rules(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["abc"],"exclude":false}]}')
    with pytest.raises(ColumnNotFoundError):
        column_selection.select(simple_data_table)


def test_exception_column_not_found_in_index_rules(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["5"],"exclude":false}],'
        '"ui":{"withRules":true}}')
    with pytest.raises(ColumnNotFoundError):
        column_selection.select(simple_data_table)


def test_exception_invalid_column_index_range_in_index_rules(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["3-1"],"exclude":false}],'
        '"ui":{"withRules":true}}')
    with pytest.raises(InvalidColumnIndexRangeError):
        column_selection.select(simple_data_table)


def test_exception_column_index_parse_in_index_rules(simple_data_table):
    column_selection = DataTableColumnSelection(
        '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["a"],"exclude":false}],'
        '"ui":{"withRules":true}}')
    with pytest.raises(ColumnIndexParsingError):
        column_selection.select(simple_data_table)


###################################
#  Column Selection Builder Test  #
###################################


def test_builder_rule_type_all_columns(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false}],"ui":{"withRules":true}}'
    column_selection = csb.include_all().build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names
    assert len(selected_data_table.meta_data.column_attributes) == len(simple_data_table.meta_data.column_attributes)
    assert selected_data_table.meta_data.column_attributes[0] == simple_data_table.meta_data.column_attributes[0]


def test_builder_rule_type_all_columns_with_include(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false},'
    # '{"ruleType":"ColumnNames","columns":["float","int"],"exclude":false}],"ui":{"withRules":true}}'
    column_selection = csb.include_all().include_col_names('float', 'int').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names


def test_builder_rule_type_all_columns_with_exclude(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"AllColumns","exclude":false},'
    # '{"ruleType":"ColumnNames","columns":["float","int"],"exclude":true}],"ui":{"withRules":true}}'
    column_selection = csb.include_all().exclude_col_names('float', 'int').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['datetime', 'string']


def test_builder_rule_type_column_name(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnNames","columns":["float","int"],"exclude":false}]}'
    column_selection = csb.include_col_names('float', 'int').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_builder_rule_type_column_indexes(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["1","2"],"exclude":false}],'
    # '"ui":{"withRules":true}}'
    column_selection = csb.include_col_indices(1, '2').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_builder_rule_type_column_indexes_range(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnIndexes","columns":["1-3"],"exclude":false}],'
    # '"ui":{"withRules":true}}'
    column_selection = csb.include_col_indices('1-3').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int', 'datetime']


def test_builder_rule_type_column_types(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Numeric"],'
    # '"columnKinds":["All"]}],"ui":{"withRules":true}}')
    column_selection = csb.include_col_types(ColumnType.NUMERIC).build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['float', 'int']


def test_builder_rule_type_column_types_with_categorical(simple_data_table):
    simple_data_table.set_column_element_type(3, ElementTypeName.CATEGORY)

    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Categorical"],'
    # '"columnKinds":["All"]}],"ui":{"withRules":true}}')
    column_selection = csb.include_col_types(ColumnType.CATEGORICAL).build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['string']


def test_builder_rule_type_column_types_with_kinds(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["All"],'
    # '"columnKinds":["Feature"]}],"ui":{"withRules":true}}')
    column_selection = csb.include_col_kinds(ColumnKind.FEATURE).build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == simple_data_table.column_names


def test_builder_rule_type_no_columns_include_and_exclude(simple_data_table):
    csb = DataTableColumnSelectionBuilder()
    # '{"isFilter":true,"rules":[{"ruleType":"ColumnTypes","exclude":false,"columnTypes":["Numeric"],'
    # '"columnKinds":["All"]},{"ruleType":"ColumnNames","columns":["float"],"exclude":true}],'
    # '"ui":{"withRules":true}}')
    column_selection = csb.include_col_types(ColumnType.NUMERIC).exclude_col_names('float').build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == ['int']


def test_builder_exception_no_columns_selected():
    with pytest.raises(NoColumnsSelectedError):
        csb = DataTableColumnSelectionBuilder()
        # '{"isFilter":true,"rules":[],"ui":{"withRules":true}}'
        csb.build()


def test_rule_type_column_name_keep_order(simple_data_table):
    col_names = ['string', 'int', 'float']
    column_selection = DataTableColumnSelectionBuilder().keep_order_and_duplicates(True).\
        include_col_names(*col_names).build()
    selected_data_table = column_selection.select(simple_data_table)
    assert selected_data_table.column_names == col_names


def test_rule_type_column_idx_keep_order():
    dt = complex_data_table()
    column_selection = DataTableColumnSelectionBuilder().keep_order_and_duplicates(True).\
        include_col_indices('3-5', '4', '1').build()
    selected_data_table = column_selection.select(dt)
    expected_names = [dt.column_names[i] for i in [2, 3, 4, 0]]
    assert selected_data_table.column_names == expected_names

    column_selection = DataTableColumnSelectionBuilder().keep_order_and_duplicates(True).\
        include_col_indices('2-4', '1-3', '6-7', '3-6').build()
    selected_data_table = column_selection.select(dt)
    expected_names = [dt.column_names[i] for i in [1, 2, 3, 0, 5, 6, 4]]
    assert selected_data_table.column_names == expected_names

    column_selection = DataTableColumnSelectionBuilder().keep_order_and_duplicates(True).\
        include_col_indices('7', '3', '2', '5').build()
    selected_data_table = column_selection.select(dt)
    expected_names = [dt.column_names[i] for i in [6, 2, 1, 4]]
    assert selected_data_table.column_names == expected_names


def test_rule_type_column_type_keep_order():
    dt = complex_data_table()
    column_selection = DataTableColumnSelectionBuilder().include_col_types(ColumnType.NUMERIC).build()
    selected_data_table = column_selection.select(dt)
    assert selected_data_table.column_names == ['int', 'float']

    dt = complex_data_table()
    column_selection = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.FEATURE).build()
    selected_data_table = column_selection.select(dt)
    assert selected_data_table.column_names == dt.column_names

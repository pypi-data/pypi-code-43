"""
Unit tests for validation.py functions
"""

# --- Standard Library Imports ------------------------------------------------
from collections import namedtuple

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
import rtm.validate.validation as val
import rtm.main.context_managers as context
from rtm.containers.fields import Fields
from rtm.containers.work_items import WorkItems


# --- General Purpose Validation ----------------------------------------------
def test_column_exist(capsys):
    io = [
        (True, "\tPass\tFIELD EXIST"),
        (False, "\tError\tFIELD EXIST"),
    ]
    for item in io:
        result = val.field_exist(item[0])
        result.print()
        captured = capsys.readouterr()
        assert item[1] in captured.out


@pytest.mark.parametrize("reverse", [False, True])
def test_column_sort(fix_fields, reverse):

    fields = fix_fields("Procedure Based Requirements")
    scores_should = ["Pass"] * len(fields)

    if reverse:
        fields = list(reversed(fields))
        scores_should = ["Pass"] + ["Error"] * (len(fields) - 1)

    with context.fields.set(fields):
        scores_actual = [val.left_right_order(field).score for field in fields]

    assert len(scores_actual) > 0
    assert scores_actual == scores_should


def test_cells_not_empty():
    passing_values = [True, False, "hello", 42]
    failing_values = [None, ""]
    values = failing_values + passing_values

    failing_indices = list(range(len(failing_values)))
    results = val.not_empty(values)
    assert results.indices == failing_indices


# --- ID ----------------------------------------------------------------------
def test_root_id_format():

    SetupRootID = namedtuple('SetupRootID', 'is_root value expected_pass')
    test_set = [
        SetupRootID(True, 'P123', True),
        SetupRootID(True, 'P123-', False),
        SetupRootID(False, 'P123-', True),
        SetupRootID(False, 'P12fd-', True),
        SetupRootID(True, 'P13-', False),
        SetupRootID(True, None, False),
        SetupRootID(True, False, False),
        SetupRootID(True, True, False),
        SetupRootID(True, 123, False),
    ]

    values = [test_item.value for test_item in test_set]
    work_items = test_set  # the function only needs the depth attribute

    expected_error_indices = [
        index
        for index, test_item in enumerate(test_set)
        if not test_item.expected_pass
    ]
    actual_error_indices = val.procedure_step_format(values, work_items).indices

    assert expected_error_indices == actual_error_indices


def test_unique_values():
    values = 'a g b c d a e f g'.split()
    expected_error_indices = [5, 8]
    assert expected_error_indices == val.unique(values).indices


def test_alphabetical_sort():
    test_sets = [
        (['a', 'b', 'c'], []),
        (['b', 'a', 'c'], [1]),
        (['c', 'b', 'a'], [1, 2]),
    ]

    for test_set in test_sets:
        input_sequence = test_set[0]
        expected_result_indices = test_set[1]
        assert expected_result_indices == val.alphabetical_sort(input_sequence).indices


# --- CASCADE BLOCK Setup -----------------------------------------------------
def get_cascade_level_not_empty():
    fields = context.fields.get()
    cascade_field = fields.get_field_object('CascadeLevel')
    results = val.not_empty(cascade_field.values)
    return results


def get_valid_cascade_levels():
    fields = context.fields.get()
    cascade_field = fields.get_field_object('CascadeLevel')
    results = val.cascade_level_valid_input(cascade_field)
    return results


ValFuncAndHeader = namedtuple("ValFuncAndHeader", "func header")
cascade_validations = [
    ValFuncAndHeader(func=val.cascade_block_not_empty, header="not_empty"),
    ValFuncAndHeader(func=val.single_entry, header="one_entry"),
    # ValFuncAndHeader(func=val.x_entry, header="x_entry"),
    ValFuncAndHeader(func=get_cascade_level_not_empty, header='cascade_level_not_empty'),
    ValFuncAndHeader(func=get_valid_cascade_levels, header='cascade_level_valid_input'),
    ValFuncAndHeader(func=val.cascade_block_match, header='cascade_level_matching'),
    ValFuncAndHeader(func=val.start_w_root_id, header='non_root_ids_start_w_root_id'),
]


# --- CASCADE BLOCK -----------------------------------------------------------
@pytest.mark.parametrize("cascade_validation", cascade_validations)
def test_rtm_xlsx_cascade(fix_worksheet_columns, cascade_validation: ValFuncAndHeader):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()
    with context.fields.set(fields):
        work_items = WorkItems()

    # Expected result
    col_with_expected_results = cascade_validation.header
    indices_expected_to_fail = [
        index
        for index, value in enumerate(ws_cols.get_first(col_with_expected_results).values)
        if not value
    ]

    # Compare
    val_func = cascade_validation.func
    with context.fields.set(fields), context.work_items.set(work_items):
        indices_that_actually_fail = list(val_func().indices)
    assert indices_that_actually_fail == indices_expected_to_fail


def test_val_cascade_block_use_all_levels(fix_worksheet_columns):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()
    with context.fields.set(fields):
        work_items = WorkItems()

    with context.fields.set(fields), context.work_items.set(work_items):
        assert val.use_all_columns().score == "Warning"


def test_val_matching_cascade_levels():
    pass


# --- REQUIREMENT STATEMENT ---------------------------------------------------
@pytest.mark.parametrize("missing_custom_input", [
    ValFuncAndHeader(func=val.missing_tags, header='missing base_found'.split()),
    ValFuncAndHeader(func=val.custom_tags, header=['custom']),
])
def test_missing_and_custom_tags(fix_worksheet_columns, missing_custom_input: ValFuncAndHeader):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()

    # Validation Result
    with context.fields.set(fields):
        val_func = missing_custom_input.func
        val_result = val_func()

    for header in missing_custom_input.header:
        expected_result = sorted(list(
            value
            for value in ws_cols.get_first(header).values
            if value is not None
        ))
        actual_result = sorted(list(
            val_result.__getattribute__(header)
        ))
        assert actual_result == expected_result


@pytest.mark.parametrize("mutual_connect_input", [
    ValFuncAndHeader(func=val.parent_child_modifiers, header='connected_edges'),
    ValFuncAndHeader(func=val.mutual_parent_child, header='mutual_edges'),
])
def test_edges(fix_worksheet_columns, mutual_connect_input: ValFuncAndHeader):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()

    # Validation Result
    with context.fields.set(fields):
        val_func = mutual_connect_input.func
        val_result = val_func()

    expected_indices = [
        index
        for index, value in enumerate(ws_cols.get_first(mutual_connect_input.header).values)
        if not value
    ]
    actual_indices = val_result.indices

    assert actual_indices == expected_indices


if __name__ == "__main__":
    pass

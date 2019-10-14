# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context
import rtm.containers.fields as cfields


def test_init_fields_list(fix_worksheet_columns):
    """Test internals of Fields class constructor"""
    field_classes = cfields.Fields.field_classes
    with context.worksheet_columns.set(fix_worksheet_columns("Procedure Based Requirements")):
        fields = [field_class() for field_class in field_classes]
        # debug

        fields_not_found = [field for field in fields if not field.found]
        print(fields_not_found)
        assert len(fields_not_found) == 0

        # resume
        fields_found = [field for field in fields if field.found]
        assert len(fields_found) == len(fields)


def test_init_fields_class(fix_worksheet_columns):
    """Test constructor of Fields class"""
    with context.worksheet_columns.set(fix_worksheet_columns("Procedure Based Requirements")):
        fields = cfields.Fields()
        fields_found = [field for field in fields if field.found]
        assert len(fields_found) == len(fields)


def test_fields_reverse(fix_worksheet_columns):
    with context.worksheet_columns.set(fix_worksheet_columns("Procedure Based Requirements")):
        fields = cfields.Fields()
        fields_reverse = list(reversed(fields))
        assert fields[0] == fields_reverse[-1]
        assert len(fields) == len(fields_reverse)


def test_fields_not_found(fix_fields):
    """Fields should all initialize to 'not found'"""
    fields = fix_fields("nonsense_fields")
    result_actual = [field.found for field in fields]
    result_expected = [False] * len(fields)
    assert result_actual == result_expected


def test_cascade_block(fix_worksheet_columns):
    with context.worksheet_columns.set(fix_worksheet_columns("Procedure Based Requirements2")):
        cascade_block = cfields.CascadeBlock()
    assert len(cascade_block) == 6
    assert cascade_block.values == [(1,2,3)]*6
    assert cascade_block.found
    assert cascade_block.position_left < cascade_block.position_right
    assert cascade_block.name == "Cascade Block"


def test_cascade_block_not_found(fix_worksheet_columns):
    fields = fix_worksheet_columns("nonsense_fields")
    with context.worksheet_columns.set(fields):
        cascade_block = cfields.CascadeBlock()
        assert len(cascade_block) == 0
        assert cascade_block.values == []
        assert not cascade_block.found
        assert cascade_block.position_left == -1
        assert cascade_block.position_right == -1
        assert cascade_block.name == "Cascade Block"

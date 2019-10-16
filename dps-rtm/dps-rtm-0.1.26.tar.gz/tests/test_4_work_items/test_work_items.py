# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context
import rtm.containers.fields
from rtm.containers.work_items import WorkItems


def test_work_items(fix_worksheet_columns):

    # --- SETUP ---------------------------------------------------------------

    # Get Worksheet Columns from worksheet:
    ws_cols = fix_worksheet_columns("cascade")

    # Get Fields from Worksheet Columns:
    with context.worksheet_columns.set(ws_cols):
        fields = rtm.containers.fields.Fields()

    # Get Work Items from Fields:
    with context.fields.set(fields):
        work_items = WorkItems()

    # --- TEST ----------------------------------------------------------------

    # Expected indices of parent work items:
    expected_parent_indices = list(ws_cols.get_first('parent').values)

    # Actual indices of parent work items:
    with context.fields.set(fields), context.work_items.set(work_items):
        actual_parent_indices = [item.parent.index for item in work_items]

    assert expected_parent_indices == actual_parent_indices


def test_work_item_index_count(fix_fields):
    fields = fix_fields("cascade")
    assert fields.height == 25

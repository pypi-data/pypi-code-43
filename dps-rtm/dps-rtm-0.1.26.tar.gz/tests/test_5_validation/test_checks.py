"""Test all funcs in rtm.validate.checks"""

import collections
import pytest
import rtm.validate.checks as checks
from rtm.containers.worksheet_columns import get_matching_worksheet_columns


def test_cell_empty():
    """checks.cell_empty is tested indirectly via test_validation.test_cells_not_empty
    No need to checks it again here.
    """
    pass


# --- Test id_prefix_format ---------------------------------------------------
InputCase = collections.namedtuple('InputCase', 'value expected_result')


@pytest.mark.parametrize('self_id', [
    InputCase('P123-1230', True),
    InputCase('P123', True),
    InputCase(True, False),
    InputCase(False, False),
    InputCase('123', False),
    InputCase(123, False),
    InputCase(None, False),
])
@pytest.mark.parametrize('root_id', [
    InputCase('P123', True),
    InputCase('P1234', False),
    InputCase(True, False),
    InputCase(False, False),
    InputCase('456', False),
    InputCase(456, False),
    InputCase(None, False),
])
def test_id_prefix_format(self_id, root_id):
    expected_result = self_id.expected_result and root_id.expected_result
    assert expected_result == checks.id_prefix_format(self_id.value, root_id.value)


# def test_get_tags(fix_worksheet_columns):
#
#     # --- Expected Results ----------------------------------------------------
#     expected_tags = dict()
#     expected_tags[0] = {
#         'SecondLineWithModifier': 'abc',
#         'ThirdLineNoModifier': '',
#     }
#     expected_tags[2] = {'FirstLineAfterWhiteSpace': ''}
#
#     # --- Actual Results ------------------------------------------------------
#     ws_cols = fix_worksheet_columns("tags")
#     req_statement = get_matching_worksheet_columns(ws_cols, 'ReqStatement')
#     values = req_statement[0].values
#     actual_tags = checks.get_tags(values)
#
#     # --- Compare -------------------------------------------------------------
#     assert actual_tags == expected_tags

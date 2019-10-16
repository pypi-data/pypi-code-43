"""This just runs the entire RTM Validator to make sure that no errors occur."""

# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.api as api


# @pytest.mark.skip('messes with coverage report')
def test_smoke_test(fix_path):

    api.main(path=fix_path, highlight_bool=True)
    assert True

import pytest

from seeq import spy

from ...tests import test_common
from . import test_load


def setup_module():
    test_common.login()


@pytest.mark.system
def test_push():
    workbooks = test_load.load_example_export()

    # Make sure the Topic is processed first, so that we test the logic that ensures all Topic dependencies are
    # pushed before the Topic is pushed. (Otherwise the IDs in the Topic will not be properly replaced.)
    reordered_workbooks = list()
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Topic', workbooks))
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Analysis', workbooks))

    with pytest.raises(Exception):
        # This will produce a 'token recognition error' for the item called 'This Formula Will Have an Error'
        spy.workbooks.push(reordered_workbooks)

    status_df = spy.workbooks.push(reordered_workbooks, errors='catalog')

    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']

    assert 'token recognition error' in analysis_result

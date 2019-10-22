import pytest

from seeq import spy

from ...tests import test_common
from . import test_load


def setup_module():
    test_common.login()


@pytest.mark.system
def test_search():
    workbooks = test_load.load_example_export()
    spy.workbooks.push(workbooks, path='My Import', errors='catalog')
    workbooks_df = spy.workbooks.search({
        'Path': 'My Import'
    })
    assert len(workbooks_df) == 2

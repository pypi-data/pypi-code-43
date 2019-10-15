import pytest

from seeq import spy

from ...tests import test_common


def setup_module():
    test_common.login()


@pytest.mark.system4
def test_search():
    spy.login('mark.derbecker@seeq.com', 'SeeQ2013!')
    results_df = spy.workbooks.search(path='Swap Folder', all_properties=True, recursive=True)
    print(results_df)

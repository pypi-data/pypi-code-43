import pytest

from seeq import spy

from . import test_common


def setup_module():
    test_common.login()


@pytest.mark.system
def test_search():
    results_df = spy.workbooks.search(recursive=True)
    print(results_df)

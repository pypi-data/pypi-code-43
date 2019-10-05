import pytest

from seeq import spy

from . import test_common


def setup_module():
    test_common.login()


@pytest.mark.system
def test_get_folder():
    results_df = spy.workbooks.get_folder(recursive=True)

    print(results_df)

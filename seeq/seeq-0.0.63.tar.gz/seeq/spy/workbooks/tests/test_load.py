import os
import pytest

from seeq import spy

from ...tests import test_common


def setup_module():
    test_common.login()


def get_example_export_path():
    return os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Documentation', 'Example Export')


def load_example_export():
    return spy.workbooks.load(get_example_export_path())


@pytest.mark.system
def test_load():
    workbooks = load_example_export()
    assert len(workbooks) == 2

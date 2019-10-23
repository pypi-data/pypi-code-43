import pytest

from seeq import spy

from ...tests import test_common
from . import test_load


def setup_module():
    test_common.login()


@pytest.mark.system8
def test_pull():
    workbook_df = spy.workbooks.search({
    })

    workbooks = spy.workbooks.pull(workbook_df)

    spy.workbooks.options.pretty_print_html = True

    spy.workbooks.save(workbooks, r'D:\Scratch\WorkbookExport')

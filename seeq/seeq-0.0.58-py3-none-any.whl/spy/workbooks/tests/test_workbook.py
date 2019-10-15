import pytest

from seeq import spy

from ...tests import test_common


def setup_module():
    # test_common.login()
    pass


@pytest.mark.system2
def test_save_load():
    # spy.login(url='https://explore.seeq.com', username='mark.derbecker@seeq.com', password='RR!Harley',
    # ignore_ssl_errors=True)

    spy.login(username='mark.derbecker@seeq.com', password='SeeQ2013!')

    search_df = spy.workbooks.search({
        'Path': 'Swap Folder'
    })

    pull_df = spy.workbooks.pull(search_df)
    spy.workbooks.save(pull_df, r'D:\Scratch\WorkbookExport2', clean=True)

    #pull_df = spy.workbooks.load(r'D:\Scratch\WorkbookExport2')
    #status_df = spy.workbooks.push(pull_df, use_full_path=True, to_original_owner=True, replace_acl=True)

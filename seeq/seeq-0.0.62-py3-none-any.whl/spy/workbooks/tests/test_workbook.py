import pytest

from seeq import spy

from ...tests import test_common


def setup_module():
    # test_common.login()
    pass


@pytest.mark.system2
def test_save_load():
    spy.login(credentials_file=r'D:\Scratch\local.key')

    search_df = spy.workbooks.search({
        'Path': 'Swap Folder'
    })

    # pull_df = spy.workbooks.pull(search_df)
    # spy.workbooks.save(pull_df, r'D:\Scratch\WorkbookExport2', clean=True)

    pull_df = spy.workbooks.load(r'D:\Scratch\WorkbookExport2')
    status_df = spy.workbooks.push(pull_df, use_full_path=True, to_original_owner=True, replace_acl=True,
                                   override_max_interp=True, label='blah')

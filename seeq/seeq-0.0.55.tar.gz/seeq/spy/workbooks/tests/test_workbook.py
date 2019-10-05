import pytest

from seeq import spy

from ...tests import test_common


def setup_module():
    # test_common.login()
    pass


@pytest.mark.system2
def test_save_load():
    #spy.login(url='https://explore.seeq.com', username='mark.derbecker@seeq.com', password='RR!Harley',
              #ignore_ssl_errors=True)

    spy.login(username='mark.derbecker@seeq.com', password='SeeQ2013!')

    #search_df = spy.workbooks.search({
        #'ID': 'B57CBDEA-BD0C-45AF-B2DE-C86CE55EEC51'
    #})

    #pull_df = spy.workbooks.pull(search_df)
    #spy.workbooks.save(pull_df, r'D:\Scratch\WorkbookExport3')

    #spy.login('mark.derbecker@seeq.com', 'SeeQ2013!', url='http://localhost:34216')

    pull_df = spy.workbooks.load(r'D:\Scratch\WorkbookExport3\Analysis 1 (B57CBDEA-BD0C-45AF-B2DE-C86CE55EEC51)')
    status_df = spy.workbooks.push(pull_df)

    # workbooks = spy.workbooks.load(r'D:\Scratch\WorkbookExport2')
    # spy.workbooks.push(workbooks)

import pytest

import pandas as pd

from seeq import spy
from seeq.sdk43.rest import ApiException

from . import test_common

from .. import _common


def setup_module():
    test_common.login()


@pytest.mark.system
def test_simple_search():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    })

    assert len(search_results) == 1

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temper'
    }]))

    # Nothing will be returned because we use a equal-to comparison when a DataFrame is passed in
    assert len(search_results) == 0

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature'
    }]))

    assert len(search_results) == 1


@pytest.mark.system
def test_dataframe_single_row_with_id():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    })

    search_results = spy.search(search_results.iloc[0])

    assert len(search_results) == 1
    assert search_results.iloc[0]['Name'] == 'Area A_Temperature'
    assert search_results.iloc[0]['Data ID'] == '[Tag] Area A_Temperature.sim.ts.csv'


@pytest.mark.system
def test_dataframe_multi_row():
    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature',
        'Datasource Name': 'Example Data'
    }, {
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity'
    }]))

    assert len(search_results) == 2
    assert len(search_results[search_results['Name'] == 'Area A_Temperature']) == 1
    assert len(search_results[search_results['Name'] == 'Relative Humidity']) == 1


@pytest.mark.system
def test_path_with_datasource():
    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity',
        'Datasource Name': 'Example Data'
    })

    assert len(search_results) == 1
    assert len(search_results[search_results['Name'] == 'Relative Humidity']) == 1

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity',
        'Datasource Name': 'Seeq Database',
        'Datasource Class': 'cassandraV2'
    })

    assert len(search_results) == 0


@pytest.mark.system
def test_dataframe_bad_datasource():
    with pytest.raises(RuntimeError):
        spy.search(pd.DataFrame([{
            'Name': 'Area A_Temperature',
            'Datasource Name': 'Bad Datasource'
        }]))


@pytest.mark.system
def test_type_search():
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Signal'
    })

    assert 150 < len(search_results) < 200

    datasource_names = set(search_results['Datasource Name'].tolist())
    assert len(datasource_names) == 1
    assert datasource_names.pop() == 'Example Data'

    types = set(search_results['Type'].tolist())
    assert len(types) == 1
    assert types.pop() == 'StoredSignal'

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Condition'
    })

    assert len(search_results) == 0

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Scalar'
    })

    assert len(search_results) == 0

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Asset'
    })

    assert 5 < len(search_results) < 20

    # Multiple types
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': ['Signal', 'Asset']
    })

    assert 160 < len(search_results) < 300
    assert 5 < len(search_results[search_results['Type'] == 'Asset']) < 20
    assert 150 < len(search_results[search_results['Type'].str.contains('Signal')]) < 200


@pytest.mark.system
def test_path_search_recursive():
    with pytest.raises(RuntimeError):
        spy.search({
            'Path': 'Non-existent >> Path'
        })

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1'
    })

    assert 40 < len(search_results) < 60


@pytest.mark.system
def test_path_search_non_recursive():
    with pytest.raises(RuntimeError):
        spy.search({
            'Name': 'Blah',
            'Path': 'Example >> Cooling Tower 1'
        }, recursive=False)

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1'
    }, recursive=False, workbook=None)

    assert 5 < len(search_results) < 10


@pytest.mark.system
def test_path_search_pagination():
    # This tests the 'Path' finding code to make sure we'll find a path even if pagination
    # is required.
    original_page_size = _common.DEFAULT_SEARCH_PAGE_SIZE
    try:
        _common.DEFAULT_SEARCH_PAGE_SIZE = 1
        search_results = spy.search({
            'Path': 'Example >> Cooling Tower 1 >> Area G'
        }, recursive=False, workbook=None)

        assert len(search_results) == 6
    finally:
        _common.DEFAULT_SEARCH_PAGE_SIZE = original_page_size


@pytest.mark.system
def test_path_search_bad_path():
    try:
        spy.search({
            'Path': 'Exclample >> Cooling Tower Bogus'
        }, recursive=False)

        assert False, 'Expected RuntimeError exception'

    except RuntimeError as e:
        error_string = str(e)
        assert 'Could not find item "Exclample" as root asset' in error_string
        assert '"Example"' in error_string

    try:
        spy.search({
            'Path': 'Example >> Cooling Tower Bogus'
        }, recursive=False)

        assert False, 'Expected RuntimeError exception'

    except RuntimeError as e:
        assert 'Could not find item "Cooling Tower Bogus" under "Example"' in str(e)
        assert '"Cooling Tower 1"' in str(e)
        assert '"Cooling Tower 2"' in str(e)


@pytest.mark.system
def test_datasource_name_search():
    with pytest.raises(RuntimeError):
        spy.search({
            'Datasource Name': 'Non-existent'
        })

    search_results = spy.search({
        'Datasource Name': 'Example Data'
    })

    assert 150 < len(search_results) < 200


@pytest.mark.system
def test_search_pagination():
    original_page_size = _common.DEFAULT_SEARCH_PAGE_SIZE
    try:
        _common.DEFAULT_SEARCH_PAGE_SIZE = 2
        search_results = spy.search({
            'Name': 'Area A_*'
        })

        assert len(search_results) == 6

    finally:
        _common.DEFAULT_SEARCH_PAGE_SIZE = original_page_size


@pytest.mark.system
def test_search_bad_workbook():
    with pytest.raises(RuntimeError):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='bad')


@pytest.mark.system
def test_search_workbook_guid():
    # The workbook won't be found, so we'll get an access error
    with pytest.raises(ApiException):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='A0B89103-E95D-4E32-A809-390C1FAE9D2F')

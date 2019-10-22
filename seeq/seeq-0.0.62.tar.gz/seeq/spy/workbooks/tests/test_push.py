import os
import pytest

from seeq import spy
from seeq.sdk import *

from ...tests import test_common
from . import test_load


def setup_module():
    test_common.login()


def _load_and_push(subfolder):
    full_path = os.path.join(os.path.dirname(__file__), subfolder)
    workbooks = spy.workbooks.load(full_path)
    return _push(workbooks)


def _push(workbooks):
    push_df = spy.workbooks.push(workbooks)
    return push_df.iloc[0]['Pushed Workbook ID']


@pytest.mark.system
def test_push():
    workbooks = test_load.load_example_export()

    # Make sure the Topic is processed first, so that we test the logic that ensures all Topic dependencies are
    # pushed before the Topic is pushed. (Otherwise the IDs in the Topic will not be properly replaced.)
    reordered_workbooks = list()
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Topic', workbooks))
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Analysis', workbooks))

    with pytest.raises(Exception):
        # This will produce a 'token recognition error' for the item called 'This Formula Will Have an Error'
        spy.workbooks.push(reordered_workbooks)

    status_df = spy.workbooks.push(reordered_workbooks, errors='catalog')

    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']

    assert 'token recognition error' in analysis_result


@pytest.mark.system
def test_bad_metric():
    pushed_workbook_id = _load_and_push('Bad Metric')

    metrics_api = MetricsApi(test_common.get_client())

    # To see the code that this exercises, search for test_bad_metric in _workbook.py
    metric_item = spy.workbooks.Workbook.find_item('3ED7F847-61DA-4359-95FA-E6C2E5421DC9',
                                                   workbook_id=pushed_workbook_id)
    threshold_metric_output = metrics_api.get_metric(id=metric_item.id)  # type: ThresholdMetricOutputV1
    assert threshold_metric_output.bounding_condition_maximum_duration.value == 40
    assert threshold_metric_output.bounding_condition_maximum_duration.uom == 'h'

    metric_item = spy.workbooks.Workbook.find_item('6B09312E-CC40-4264-A3F2-A78673F6148B',
                                                   workbook_id=pushed_workbook_id)
    threshold_metric_output = metrics_api.get_metric(id=metric_item.id)  # type: ThresholdMetricOutputV1
    assert threshold_metric_output.measured_item_maximum_duration.value == 40
    assert threshold_metric_output.measured_item_maximum_duration.uom == 'h'


@pytest.mark.system
def test_ancillaries():
    pushed_workbook_id = _load_and_push('Ancillaries')

    items_api = ItemsApi(test_common.get_client())

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Temperature.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    temp_upper = spy.workbooks.Workbook.find_item('018335D9-42AC-4ED2-A8EC-4A5362EC084E',
                                                  workbook_id=pushed_workbook_id)
    temp_lower = spy.workbooks.Workbook.find_item('82006DDE-57E4-4299-843B-46EE4B6A4160',
                                                  workbook_id=pushed_workbook_id)

    assert len(item_output.ancillaries) == 1
    assert len(item_output.ancillaries[0].items) == 2
    for ancillary_item in item_output.ancillaries[0].items:  # type: ItemAncillaryOutputV1
        if ancillary_item.name == 'Temperature Warning Upper':
            assert ancillary_item.id == temp_upper.id
        if ancillary_item.name == 'Temperature Warning Lower':
            assert ancillary_item.id == temp_lower.id

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Relative Humidity.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    humid_upper = spy.workbooks.Workbook.find_item('FACB7074-35A5-415F-BD9A-6FFDC33F6FCB',
                                                   workbook_id=pushed_workbook_id)
    humid_lower = spy.workbooks.Workbook.find_item('C56CDE81-8E8A-4287-ADB5-9E40180CE3A6',
                                                   workbook_id=pushed_workbook_id)

    assert len(item_output.ancillaries) == 1
    assert len(item_output.ancillaries[0].items) == 2
    for ancillary_item in item_output.ancillaries[0].items:  # type: ItemAncillaryOutputV1
        if ancillary_item.name == 'Relative Humidity Warning Upper':
            assert ancillary_item.id == humid_upper.id
        if ancillary_item.name == 'Relative Humidity Warning Lower':
            assert ancillary_item.id == humid_lower.id

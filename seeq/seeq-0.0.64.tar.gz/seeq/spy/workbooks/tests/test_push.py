import json
import os
import pytest

from seeq import spy
from seeq.sdk import *

from ...tests import test_common
from . import test_load


def setup_module():
    test_common.login()


def _get_exports_folder():
    return os.path.join(os.path.dirname(__file__), 'Exports')


def _get_full_path_of_export(subfolder):
    return os.path.join(_get_exports_folder(), subfolder)


def _load_and_push(subfolder):
    workbooks = spy.workbooks.load(_get_full_path_of_export(subfolder))
    return _push(workbooks)


def _push(workbooks):
    push_df = spy.workbooks.push(workbooks)
    return push_df.iloc[0]['Pushed Workbook ID']


@pytest.mark.export
def test_export_example_and_test_data():
    # Use this function to re-create the Example Export and test-related exports.
    # First copy the contents of "crab/sdk/pypi/spy-example-and-test-data-folder.zip" into "crab/sq-run-data-dir"
    # and start Seeq Server by doing "sq run" from crab.
    #
    # You can log in as "mark.derbecker@seeq.com" with password "SeeQ2013!". If you add workbooks, make sure to share
    # them with Everyone because the tests will log in as Agent API Key.
    #
    # When finished, change the sdk-system-tests Run Configuration in IntelliJ to have an "-m export" flag so that only
    # this test gets executed. It will copy everything into the right spot.
    #
    # Then make sure to zip up the contents of "crab/sq-run-data-dir" and replace
    # "crab/sdk/pypi/spy-example-and-test-data-folder.zip" and commit it to the repo.

    search_df = spy.workbooks.search({
        'Path': 'Example Export'
    }, content_filter='ALL')

    workbooks = spy.workbooks.pull(search_df)
    spy.workbooks.save(workbooks, test_load.get_example_export_path(), clean=True)

    search_df = spy.workbooks.search({}, content_filter='ALL')

    workbooks = spy.workbooks.pull(search_df)
    spy.workbooks.save(workbooks, _get_exports_folder(), clean=True)

    _delete_max_capsule_duration_on_bad_metric()


@pytest.mark.system
def test_example_export():
    workbooks = test_load.load_example_export()

    # Make sure the Topic is processed first, so that we test the logic that ensures all Topic dependencies are
    # pushed before the Topic is pushed. (Otherwise the IDs in the Topic will not be properly replaced.)
    reordered_workbooks = list()
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Topic', workbooks))
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Analysis', workbooks))

    status_df = spy.workbooks.push(reordered_workbooks)

    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']

    assert 'Success' in analysis_result


def _delete_max_capsule_duration_on_bad_metric():
    with open(os.path.join(_get_exports_folder(),
                           'Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)', 'Items.json'), 'r') as f:
        bad_metrics_items_json = json.load(f)

    del bad_metrics_items_json['1541C121-A38E-41C3-BFFA-AB01D0D0F30C']["Formula Parameters"][
        "Measured Item Maximum Duration"]

    del bad_metrics_items_json['1AA91F16-D476-4AF8-81AB-A2120FDA68E5']["Formula Parameters"][
        "Bounding Condition Maximum Duration"]

    with open(os.path.join(_get_exports_folder(),
                           'Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)', 'Items.json'), 'w') as f:
        json.dump(bad_metrics_items_json, f, indent=4)


@pytest.mark.system
def test_bad_metric():
    pushed_workbook_id = _load_and_push('Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)')

    metrics_api = MetricsApi(test_common.get_client())

    # To see the code that this exercises, search for test_bad_metric in _workbook.py
    metric_item = spy.workbooks.Workbook.find_item('1AA91F16-D476-4AF8-81AB-A2120FDA68E5',
                                                   workbook_id=pushed_workbook_id)
    threshold_metric_output = metrics_api.get_metric(id=metric_item.id)  # type: ThresholdMetricOutputV1
    assert threshold_metric_output.bounding_condition_maximum_duration.value == 40
    assert threshold_metric_output.bounding_condition_maximum_duration.uom == 'h'

    metric_item = spy.workbooks.Workbook.find_item('1541C121-A38E-41C3-BFFA-AB01D0D0F30C',
                                                   workbook_id=pushed_workbook_id)
    threshold_metric_output = metrics_api.get_metric(id=metric_item.id)  # type: ThresholdMetricOutputV1
    assert threshold_metric_output.measured_item_maximum_duration.value == 40
    assert threshold_metric_output.measured_item_maximum_duration.uom == 'h'


@pytest.mark.system
def test_ancillaries():
    pushed_workbook_id = _load_and_push('Ancillaries (54C62C9E-629B-4A76-B8D6-5348D7D59D5F)')

    items_api = ItemsApi(test_common.get_client())

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Wet Bulb.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    wet_bulb_upper = spy.workbooks.Workbook.find_item('C33AB410-7B16-41FA-A374-BEB63900A857',
                                                      workbook_id=pushed_workbook_id)
    wet_bulb_lower = spy.workbooks.Workbook.find_item('67796251-BE83-4047-975E-89D5D5858814',
                                                      workbook_id=pushed_workbook_id)

    assert len(item_output.ancillaries) == 1
    assert len(item_output.ancillaries[0].items) == 2
    for ancillary_item in item_output.ancillaries[0].items:  # type: ItemAncillaryOutputV1
        if ancillary_item.name == 'Wet Bulb Warning Upper':
            assert ancillary_item.id == wet_bulb_upper.id
        if ancillary_item.name == 'Wet Bulb Warning Lower':
            assert ancillary_item.id == wet_bulb_lower.id

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Relative Humidity.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    humid_upper = spy.workbooks.Workbook.find_item('C2334AD9-4152-4CAA-BCA6-728A56E47F16',
                                                   workbook_id=pushed_workbook_id)
    humid_lower = spy.workbooks.Workbook.find_item('A33334D3-6E92-40F2-80E3-95B18D08FAF2',
                                                   workbook_id=pushed_workbook_id)

    # Because Relative Humidity is not present on any worksheets, the ancillary will not have been pushed. The
    # upper/lower boundary signals will have been pushed though.
    assert len(item_output.ancillaries) == 0
    assert humid_upper is not None
    assert humid_lower is not None


@pytest.mark.system
def test_archived_worksheets():
    workbooks = list()
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Archived Worksheet - Topic (F662395E-FEBB-4772-8B3B-B2D7EB7C0C3B)')))
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Archived Worksheet - Analysis (DDB5F823-3B6A-42DC-9C44-566466C2BA82)')))

    push_df = spy.workbooks.push(workbooks)

    pushed_workbook_id = push_df.iloc[0]['Pushed Workbook ID']

    archived_worksheet = spy.workbooks.Workbook.find_item('C28D3F17-C7BB-43B7-B670-41550D623CDF',
                                                          workbook_id=pushed_workbook_id)

    items_api = ItemsApi(test_common.get_client())
    assert items_api.get_property(id=archived_worksheet.id, property_name='Archived').value

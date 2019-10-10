import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
from tests.config import (NEW_VIRTUAL_ACCOUNT_PAYLOAD)
import time
from functools import reduce


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.pnp
def test_get_smart_account_list(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_3cb24acb486b89d2_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_virtual_account_list(runner, cli, auth_options):
    smart_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    smart_account_list = loads(smart_account_list.output)

    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-virtual-account-list', '--domain', smart_account_list[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_70a479a6462a9496_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([NEW_VIRTUAL_ACCOUNT_PAYLOAD]) is True,
                    reason="tests.config values required not present")
@pytest.mark.pnp
def test_add_virtual_account(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'add-virtual-account', '--payload', dumps(NEW_VIRTUAL_ACCOUNT_PAYLOAD), '--active_validation', False])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_1e962af345b8b59f_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_sync_result_for_virtual_account(runner, cli, auth_options):
    smart_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    smart_account_list = loads(smart_account_list.output)

    virtual_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-virtual-account-list', '--domain', smart_account_list[0]])
    virtual_account_list = loads(virtual_account_list.output)

    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-sync-result-for-virtual-account', '--domain', smart_account_list[0], '--name', virtual_account_list[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_0a9c988445cb91c8_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_update_pnp_server_profile(runner, cli, auth_options):
    smart_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    smart_account_list = loads(smart_account_list.output)

    virtual_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-virtual-account-list', '--domain', smart_account_list[0]])
    virtual_account_list = loads(virtual_account_list.output)

    sync_result = runner.invoke(cli, [*auth_options, 'pnp', 'get-sync-result-for-virtual-account', '--domain', smart_account_list[0], '--name', virtual_account_list[0]])
    sync_result = sync_result.output

    result = runner.invoke(cli, [*auth_options, 'pnp', 'update-pnp-server-profile', '--payload', sync_result, '--active_validation', False])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_6f9819e84178870c_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_sync_virtual_account_devices(runner, cli, auth_options):
    smart_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    smart_account_list = loads(smart_account_list.output)

    virtual_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-virtual-account-list', '--domain', smart_account_list[0]])
    virtual_account_list = loads(virtual_account_list.output)

    sync_result = runner.invoke(cli, [*auth_options, 'pnp', 'get-sync-result-for-virtual-account', '--domain', smart_account_list[0], '--name', virtual_account_list[0]])
    sync_result = sync_result.output

    result = runner.invoke(cli, [*auth_options, 'pnp', 'sync-virtual-account-devices', '--payload', sync_result, '--active_validation', False])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a4b6c87a4ffb9efa_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_deregister_virtual_account(runner, cli, auth_options):
    time.sleep(20)
    smart_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-smart-account-list'])
    smart_account_list = loads(smart_account_list.output)

    virtual_account_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-virtual-account-list', '--domain', smart_account_list[0]])
    virtual_account_list = loads(virtual_account_list.output)

    result = runner.invoke(cli, [*auth_options, 'pnp', 'deregister-virtual-account', '--domain', smart_account_list[0], '--name', virtual_account_list[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_2499e9ad42e8ae5b_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_workflow_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflow-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7989f86846faaf99_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_workflows(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--sort', 'addedOn', '--sort_order', 'des'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_aeb4dad04a99bbe3_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_pnp_global_settings(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-pnp-global-settings'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7e92f9eb46db8320_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_update_pnp_global_settings(runner, cli, auth_options):
    pnp_global_settings = runner.invoke(cli, [*auth_options, 'pnp', 'get-pnp-global-settings'])
    pnp_global_settings = pnp_global_settings.output

    result = runner.invoke(cli, [*auth_options, 'pnp', 'update-pnp-global-settings', '--payload', pnp_global_settings, '--active_validation', False])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8da0391947088a5a_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_device_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d9a1fa9c4068b23c_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_import_devices_in_bulk(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'import-devices-in-bulk',
                                 '--payload', dumps([{
                                     "deviceInfo": {
                                         "serialNumber": "c3160d2650",
                                         "name": "Test device c3160d2650"
                                     }
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_21a6db2540298f55_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_device_list(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--limit', 1])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_e6b3db8046c99654_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_device_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--limit', 1])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-by-id', '--id', device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_bab6c9e5440885cc_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_device_history(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--limit', 1])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-history', '--serial_number', device_list[0].deviceInfo.serialNumber])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f09319674049a7d4_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_add_device_2(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'add-device', '--deviceinfo', dumps({'serialNumber': 'FJC2048D0HX', 'name': 'catalyst_ap_test', 'pid': 'ISR4431-SEC/K9'})])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_f3b26b5544cabab9_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_preview_config(runner, cli, auth_options):
    sites = runner.invoke(cli, [*auth_options, 'sites', 'get-site-health'])
    sites = mydict_data_factory('', loads(sites.output)).response
    sites = list(filter(lambda x: x.siteType == 'building', sites))
    siteId = sites[-1].siteId if len(sites) > 0 else "1"

    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'preview-config', '--deviceid', device_list[0].id, '--siteid', siteId, '--type', 'Default'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cf9418234d9ab37e_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_claim_a_device_to_a_site(runner, cli, auth_options):
    sites = runner.invoke(cli, [*auth_options, 'sites', 'get-site-health'])
    sites = mydict_data_factory('', loads(sites.output)).response
    sites = list(filter(lambda x: x.siteType == 'building', sites))
    siteId = sites[-1].siteId if len(sites) > 0 else "1"

    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))
    deviceId = device_list[0].id

    result = runner.invoke(cli, [*auth_options, 'pnp', 'claim-a-device-to-a-site',
                                 '--payload', dumps({
                                     "siteId": siteId,
                                     "deviceId": deviceId,
                                     "type": "Default",
                                     "imageInfo": {"imageId": "", 'skip': False},
                                     "configInfo": {"configId": "", 'configParameters': []}
                                 })])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_5889fb844939a13b_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_delete_device_by_id_from_pnp_imported(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'Test device c3160d2650'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'delete-device-by-id-from-pnp', '--id', device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cdab9b474899ae06_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_add_device(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'pnp', 'add-device', '--deviceinfo', dumps({'serialNumber': 'd2650c3160', 'name': 'Test device d2650c3160'})])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f3b26b5544cabab9_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_update_device(runner, cli, auth_options):
    time.sleep(10)
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'Test device d2650c3160'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'update-device', '--id', device_list[0].id, '--deviceinfo', dumps({'name': 'Test device d2650c3160-1'})])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_09b0f9ce4239ae10_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_add_a_workflow(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output, strict=False))
    filtered_project = list(filter(lambda x: x.name == 'Onboarding Configuration', projects))

    endpoint_result = runner.invoke(cli, [*auth_options, 'template-programmer', 'create-template', '--project_id', filtered_project[0].id,
                                          '--composite', False, '--devicetypes', dumps({"productFamily": "Switches and Hubs"}),
                                          '--name', 'test_template_06',
                                          '--rollbacktemplatecontent', "",
                                          '--softwaretype', 'IOS-XE',
                                          '--softwarevariant', 'XE',
                                          '--templatecontent', 'show version\n'])

    endpoint_result = mydict_data_factory('', loads(endpoint_result.output, strict=False))
    time.sleep(10)

    task = runner.invoke(cli, [*auth_options, 'task', 'get-task-by-id', '--task_id', endpoint_result.response.taskId])

    task = mydict_data_factory('', loads(task.output, strict=False)).response
    time.sleep(5)

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', task.data])

    template = mydict_data_factory('', loads(template.output, strict=False))

    time.sleep(5)

    runner.invoke(cli, [*auth_options, 'template-programmer', 'version-template', '--templateid', template.id])
    runner.invoke(cli, [*auth_options, 'template-programmer', 'preview-template', '--templateid', template.id])
    result = runner.invoke(cli, [*auth_options, 'pnp', 'add-a-workflow', '--description', 'test_devnet_1',
                                 '--name', 'test_devnet_1', '--tasks', dumps({
                                     'taskSeqNo': 0,
                                     'name': 'Config Download',
                                     'type': 'Config',
                                     'startTime': 0,
                                     'endTime': 0,
                                     'timeTaken': 0,
                                     'currWorkItemIdx': 0,
                                     'configInfo': {
                                         'configId': template.id,
                                         'configFileUrl': None,
                                         'fileServiceId': None,
                                         'saveToStartUp': True,
                                         'connLossRollBack': True,
                                         'configParameters': None
                                     }
                                 }), '--type', 'Standard', '--usestate', 'Available'])

    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_848b5a7b4f9b8c12_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_get_workflow_by_id(runner, cli, auth_options):
    workflows = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--sort', 'addedOn', '--sort_order', 'des'])
    workflows = mydict_data_factory('', loads(workflows.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflow-by-id', '--id', workflows[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_80acb88e4ac9ac6d_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_update_workflow(runner, cli, auth_options):
    workflows = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--name', 'test_devnet_1'])

    workflow = mydict_data_factory('', loads(workflows.output))[0]

    result = runner.invoke(cli, [*auth_options, 'pnp', 'update-workflow', '--id', workflow.id, '--description', workflow.description, '--name', workflow.name,
                                 *reduce(lambda a, b: a + b, [['--tasks', dumps(x)] for x in workflow.tasks]),
                                 '--type', workflow.type, '--usestate', workflow.useState])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_3086c9624f498b85_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_claim_device(runner, cli, auth_options):
    workflows = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--name', 'test_devnet_1'])
    workflow = mydict_data_factory('', loads(workflows.output))[0]
    configList = [workflow.tasks[0].configInfo]

    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))
    deviceId = device_list[0].id

    result = runner.invoke(cli, [*auth_options, 'pnp', 'claim-device',
                                 '--deviceclaimlist', dumps(
                                     {
                                         "configList": configList,
                                         "deviceId": deviceId
                                     }
                                 ), '--workflowid', workflow.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d8a619974a8a8c48_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_un_claim_device(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))
    deviceId = device_list[0].id

    result = runner.invoke(cli, [*auth_options, 'pnp', 'un-claim-device', '--deviceidlist', deviceId])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output, strict=False)
        assert json_schema_validate('jsd_0b836b7b4b6a9fd5_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_reset_device(runner, cli, auth_options):
    workflows = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--name', 'test_devnet_1'])
    workflow = mydict_data_factory('', loads(workflows.output))[0]

    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))
    deviceId = device_list[0].id

    result = runner.invoke(cli, [*auth_options, 'pnp', 'reset-device',
                                 '--deviceresetlist', dumps({"deviceId": deviceId, 'configList': [workflow.tasks[0].configInfo]}), '--workflowid', workflow.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9e857b5a4a0bbcdb_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_delete_workflow_by_id(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output, strict=False))
    filtered_project = list(filter(lambda x: x.name == 'Onboarding Configuration', projects))

    templates = filtered_project[0].templates
    for template in templates:
        if 'test_template' in template.name:
            result = runner.invoke(cli, [*auth_options, 'template-programmer', 'delete-template', '--template_id', template.id])

    workflows = runner.invoke(cli, [*auth_options, 'pnp', 'get-workflows', '--name', 'test_devnet_1'])
    workflows = mydict_data_factory('', loads(workflows.output))
    result = runner.invoke(cli, [*auth_options, 'pnp', 'delete-workflow-by-id', '--id', workflows[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_af8d7b0e470b8ae2_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_delete_device_by_id_from_pnp_added(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'Test device d2650c3160-1'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'delete-device-by-id-from-pnp', '--id', device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cdab9b474899ae06_v1_2_10').validate(obj) is None


@pytest.mark.pnp
def test_delete_device_by_id_from_pnp_added_2(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'pnp', 'get-device-list', '--name', 'catalyst_ap_test'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'pnp', 'delete-device-by-id-from-pnp', '--id', device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cdab9b474899ae06_v1_2_10').validate(obj) is None

import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from tests.config import MERAKI_ORG_ID
from dnacentersdk import mydict_data_factory
import time

pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.devices
def test_get_device_interface_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-interface-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_3d923b184dc9a4ca_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_list(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_20b19b52464b8972_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_sync_devices_using_forcesync(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'sync-devices-using-forcesync',
                                 '--payload', '["{}"]'.format(device_list.response[0].id)])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_3b9ef9674429be4c_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_polling_interval_for_all_devices(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-polling-interval-for-all-devices'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_38bd0b884b89a785_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_5db21b8e43fab7d8_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_interface_vlans(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output)).response
    devices_filtered = [device if 'Switches and Hubs' in device.family
                        and device.interfaceCount and device.interfaceCount > "1"
                        else None for device in device_list]
    devices_filtered = list(filter(lambda x: x, devices_filtered))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-interface-vlans', '--id', devices_filtered[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_288df9494f2a9746_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_interfaces_by_specified_range(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-interfaces-by-specified-range', '--device_id', device_list.response[0].id, '--records_to_return', 1, '--start_index', 3])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_349c888443b89a58_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_config_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-config-by-id', '--network_device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_84b33a9e480abcaf_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_config_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-config-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_888f585c49b88441_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_all_interfaces(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-all-interfaces', '--limit', 500, '--offset', 1])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5947a4c439a8bf0_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_interface_details(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    devices_filtered = [device if 'Switches and Hubs' in device.family
                        and device.interfaceCount and device.interfaceCount > "1"
                        else None for device in device_list.response]
    devices_filtered = list(filter(lambda x: x, devices_filtered))
    device_interface_vlans = runner.invoke(cli, [*auth_options, 'devices', 'get-device-interface-vlans', '--id', devices_filtered[0].id])
    device_interface_vlans = mydict_data_factory('', loads(device_interface_vlans.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-interface-details', '--device_id', device_list.response[0].id, '--name', device_interface_vlans.response[0].interfaceName])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4eb56a614cc9a2d2_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_polling_interval_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-polling-interval-by-id', '--id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_82918a1b4d289c5c_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_module_count(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-module-count', '--device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8db939744649a782_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_interface_info_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-interface-info-by-id', '--device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ba9dc85b4b8a9a17_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_summary(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-summary', '--id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_819f9aa54feab7bf_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_functional_capability_for_devices(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-functional-capability-for-devices', '--device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c3b3c9ef4e6b8a09_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_interface_count_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-interface-count-by-id', '--device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_5b8639224cd88ea7_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_modules(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-modules', '--device_id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_eb8249e34f69b0f1_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_wireless_lan_controller_details_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-wireless-lan-controller-details-by-id', '--id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f6826a8e41bba242_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([MERAKI_ORG_ID]) is True,
                    reason="tests.config values required not present")
@pytest.mark.devices
def test_get_organization_list_for_meraki(runner, cli, auth_options):
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'SNMPV2_READ_COMMUNITY'])
    credentials = mydict_data_factory('', loads(credentials.output)).response
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    device_list_ips = [d.managementIpAddress for d in device_list.response]
    device_ip = device_list_ips[0]
    a = list(filter(lambda x: x.rsplit('.', 1)[0] == device_ip.rsplit('.', 1)[0], device_list_ips))
    b = set(range(2, 103)) - set([int(x.rsplit('.', 1)[-1]) for x in a])
    new_ipAddress = device_ip.rsplit('.', 1)[0] + '.' + str(list(b)[0])

    runner.invoke(cli, [*auth_options, 'devices', 'add-device',
                        '--clitransport', 'ssh',
                        '--enablepassword', 'false',
                        '--ipaddress', new_ipAddress,
                        '--merakiorgid', MERAKI_ORG_ID,
                        '--password', "W.~&KV9ha",
                        '--snmpmode', "NOAUTHNOPRIV",
                        '--snmprocommunity', credentials[0].id,
                        '--snmprwcommunity', "",
                        '--snmpretry', 0,
                        '--snmptimeout', 0,
                        '--snmpusername', "test_user_devnet",
                        '--snmpversion', "v2",
                        '--type', "NETWORK_DEVICE",
                        '--username', "test_user_devnet",
                        '--active_validation', True])
    time.sleep(10)
    filtered_device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list', '--family', 'null', '--hostname', 'null', '--software_type', 'null', '--management_ip_address', new_ipAddress])
    filtered_device_list = mydict_data_factory('', loads(filtered_device_list.output)).response
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-organization-list-for-meraki', '--id', filtered_device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_84b37ae54c59ab28_v1_2_10').validate(obj) is None
    time.sleep(10)
    filtered_device_list = runner.invoke(cli, [*auth_options, 'devices', 'delete-device-by-id', '--id', filtered_device_list[0].id])


@pytest.mark.devices
def test_get_ospf_interfaces(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-ospf-interfaces'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_70ad397649e9b4d3_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_functional_capability_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    functional_capability_devices = runner.invoke(cli, [*auth_options, 'devices', 'get-functional-capability-for-devices', '--device_id', device_list.response[0].id])
    functional_capability_devices = mydict_data_factory('', loads(functional_capability_devices.output)).response
    functional_capability = functional_capability_devices[0].functionalCapability[0]
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-functional-capability-by-id', '--id', functional_capability.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_81bb4804405a8d2f_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_isis_interfaces(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-isis-interfaces'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_84ad8b0e42cab48a_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_config_for_all_devices(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-config-for-all-devices'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b7bcaa084e2b90d0_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_interface_by_ip(runner, cli, auth_options):
    interfaces = runner.invoke(cli, [*auth_options, 'devices', 'get-all-interfaces', '--limit', 500, '--offset', 1])
    interfaces = mydict_data_factory('', loads(interfaces.output)).response
    filtered_interfaces = list(filter(lambda x: x.ipv4Address is not None, interfaces))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-interface-by-ip', '--ip_address', filtered_interfaces[0].ipv4Address])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cd8469e647caab0e_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_network_device_by_ip(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-network-device-by-ip', '--ip_address', device_list.response[0].managementIpAddress])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d0a4b88145aabb51_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-by-id', '--id', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8fa8eb404a4a8d96_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_sync_devices(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'sync-devices'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_aeb9eb67460b92df_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_interface_by_id(runner, cli, auth_options):
    get_all_interfaces = runner.invoke(cli, [*auth_options, 'devices', 'get-all-interfaces', '--limit', 500, '--offset', 1])
    get_all_interfaces = mydict_data_factory('', loads(get_all_interfaces.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-interface-by-id', '--id', get_all_interfaces.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b888792d43baba46_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_by_serial_number(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    filtered_device_list = list(filter(lambda x: x.serialNumber, device_list.response))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-by-serial-number', '--serial_number', filtered_device_list[0].serialNumber])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d888ab6d4d59a8c1_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_network_device_by_pagination_range(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-network-device-by-pagination-range', '--records_to_return', 4, '--start_index', 1])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f49548c54be8a3e2_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_retrieves_all_network_devices(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'retrieves-all-network-devices', '--hostname', device_list.response[0].hostname])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ffa748cc44e9a437_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_detail(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-detail', '--identifier', "macAddress", '--search_by', device_list.response[0].macAddress])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_89b2fb144f5bb09b_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_module_info_by_id(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-module-info-by-id', '--id', device_list.response[0].lineCardId.split(',')[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_0db7da744c0b83d8_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_add_device(runner, cli, auth_options):
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'SNMPV2_READ_COMMUNITY'])
    credentials = mydict_data_factory('', loads(credentials.output)).response
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    device_list_ips = [d.managementIpAddress for d in device_list.response]
    device_ip = device_list_ips[0]
    a = list(filter(lambda x: x.rsplit('.', 1)[0] == device_ip.rsplit('.', 1)[0], device_list_ips))
    b = set(range(2, 103)) - set([int(x.rsplit('.', 1)[-1]) for x in a])
    new_ipAddress = device_ip.rsplit('.', 1)[0] + '.' + str(list(b)[0])
    result = runner.invoke(cli, [*auth_options, 'devices', 'add-device',
                                 '--clitransport', 'ssh',
                                 '--enablepassword', 'false',
                                 '--ipaddress', new_ipAddress,
                                 '--password', "W.~&KV9ha",
                                 '--snmpmode', "NOAUTHNOPRIV",
                                 '--snmprocommunity', credentials[0].id,
                                 '--snmprwcommunity', "",
                                 '--snmpretry', 0,
                                 '--snmptimeout', 0,
                                 '--snmpusername', "test_user_devnet",
                                 '--snmpversion', "v2",
                                 '--type', "NETWORK_DEVICE",
                                 '--username', "test_user_devnet",
                                 '--active_validation', True])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4bb22af046fa8f08_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_get_device_by_id_last(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'get-device-by-id', '--id', device_list.response[-1].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8fa8eb404a4a8d96_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_update_device_role(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'update-device-role', '--id', device_list.response[0].id,
                                 '--role', device_list.response[0].role,
                                 '--rolesource', device_list.response[0].roleSource])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b9855ad54ae98156_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_register_device_for_wsa(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'register-device-for-wsa',
                                 '--macaddress', device_list.response[0].macAddress,
                                 '--serial_number', device_list.response[0].serialNumber])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c9809b6744f8a502_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_export_device_list(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    result = runner.invoke(cli, [*auth_options, 'devices', 'export-device-list',
                                 '--deviceuuids', device_list.response[0].id, '--id', device_list.response[0].id,
                                 '--operationenum', 'CREDENTIALDETAILS'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cd98780f4888a66d_v1_2_10').validate(obj) is None


@pytest.mark.devices
def test_delete_device_by_id(runner, cli, auth_options):
    filtered_device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list', '--family', 'null', '--hostname', 'null', '--software_type', 'null'])
    filtered_device_list = mydict_data_factory('', loads(filtered_device_list.output)).response
    result = runner.invoke(cli, [*auth_options, 'devices', 'delete-device-by-id', '--id', filtered_device_list[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_1c894b5848eab214_v1_2_10').validate(obj) is None

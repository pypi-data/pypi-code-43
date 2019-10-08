import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
from tests.config import BORDER_DEVICE_SDA_FABRIC_PATH


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.skipif(not all([BORDER_DEVICE_SDA_FABRIC_PATH]) is True,
                    reason="tests.config values required not present")
@pytest.mark.fabric_wired
def test_adds_border_device_in_sda_fabric(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    device = device_list.response[0]

    result = runner.invoke(cli, [*auth_options, 'fabric-wired', 'adds-border-device-in-sda-fabric', '--sda_border_device', BORDER_DEVICE_SDA_FABRIC_PATH,
                                 '--payload', dumps([{"deviceManagementIpAddress": device.managementIpAddress}])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_bead7b3443b996a7_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([BORDER_DEVICE_SDA_FABRIC_PATH]) is True,
                    reason="tests.config values required not present")
@pytest.mark.fabric_wired
def test_gets_border_device_details_from_sda_fabric(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    device = device_list.response[0]

    result = runner.invoke(cli, [*auth_options, 'fabric-wired', 'gets-border-device-details-from-sda-fabric', '--device_ip_address', device.managementIpAddress, '--sda_border_device', BORDER_DEVICE_SDA_FABRIC_PATH])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_98a39bf4485a9871_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([BORDER_DEVICE_SDA_FABRIC_PATH]) is True,
                    reason="tests.config values required not present")
@pytest.mark.fabric_wired
def test_deletes_border_device_from_sda_fabric(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    device = device_list.response[0]

    result = runner.invoke(cli, [*auth_options, 'fabric-wired', 'deletes-border-device-from-sda-fabric', '--device_ip_address', device.managementIpAddress, '--sda_border_device', BORDER_DEVICE_SDA_FABRIC_PATH])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cb81b93540baaab0_v1_2_10').validate(obj) is None

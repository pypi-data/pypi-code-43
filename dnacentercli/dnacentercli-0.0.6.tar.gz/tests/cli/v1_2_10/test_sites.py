import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.sites
def test_get_site_health(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'sites', 'get-site-health'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_17a82ac94cf99ab0_v1_2_10').validate(obj) is None


@pytest.mark.sites
def test_create_site(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'sites', 'create-site',
                                 '--payload', dumps({
                                     'type': 'building',
                                     'site': {
                                         'building': {
                                             'name': 'Test_Building',
                                             'address': '10.10.22.70'
                                         }
                                     }
                                 })])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_50b589fd4c7a930a_v1_2_10').validate(obj) is None


@pytest.mark.sites
def test_assign_device_to_site(runner, cli, auth_options):
    sites = runner.invoke(cli, [*auth_options, 'sites', 'get-site-health'])
    sites = mydict_data_factory('', loads(sites.output)).response
    siteId = sites[0].siteId if sites and len(sites) > 0 else '1'

    device = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device = mydict_data_factory('', loads(device.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'sites', 'assign-device-to-site', '--site_id', siteId, '--device', dumps({'ip': device.managementIpAddress})])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_eeb168eb41988e07_v1_2_10').validate(obj) is None

import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
from tests.config import (NEW_ENTERPRISE_SSID_NAME,
                          NEW_MANAGED_APLOCATIONS)


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.non_fabric_wireless
def test_create_enterprise_ssid(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'non-fabric-wireless', 'create-enterprise-ssid', '--payload', '{}'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8a96fb954d09a349_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([NEW_ENTERPRISE_SSID_NAME]) is True,
                    reason="tests.config values required not present")
@pytest.mark.non_fabric_wireless
def test_get_enterprise_ssid(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'non-fabric-wireless', 'get-enterprise-ssid', '--ssid_name', NEW_ENTERPRISE_SSID_NAME])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cca519ba45ebb423_v1_2_10').validate(obj) is None


@pytest.mark.non_fabric_wireless
def test_create_and_provision_ssid(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'non-fabric-wireless', 'create-and-provision-ssid', '--payload', '{}'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_db9f997f4e59aec1_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([NEW_MANAGED_APLOCATIONS, NEW_ENTERPRISE_SSID_NAME]) is True,
                    reason="tests.config values required not present")
@pytest.mark.non_fabric_wireless
def test_delete_and_provision_ssid(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'non-fabric-wireless', 'delete-and-provision-ssid', '--managed_aplocations', NEW_MANAGED_APLOCATIONS, '--ssid_name', NEW_ENTERPRISE_SSID_NAME])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_cca098344a489dfa_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([NEW_ENTERPRISE_SSID_NAME]) is True,
                    reason="tests.config values required not present")
@pytest.mark.non_fabric_wireless
def test_delete_enterprise_ssid(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'non-fabric-wireless', 'delete-enterprise-ssid', '--ssid_name', NEW_ENTERPRISE_SSID_NAME])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c7a6592b4b98a369_v1_2_10').validate(obj) is None

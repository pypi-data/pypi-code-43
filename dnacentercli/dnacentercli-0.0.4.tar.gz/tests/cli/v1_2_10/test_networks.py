import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.networks
def test_get_vlan_details(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'networks', 'get-vlan-details'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_6284db4649aa8d31_v1_2_10').validate(obj) is None


@pytest.mark.networks
def test_get_site_topology(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'networks', 'get-site-topology'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9ba14a9e441b8a60_v1_2_10').validate(obj) is None


@pytest.mark.networks
def test_get_physical_topology(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'networks', 'get-physical-topology'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b2b8cb91459aa58f_v1_2_10').validate(obj) is None


@pytest.mark.networks
def test_get_l3_topology_details(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'networks', 'get-l3-topology-details', '--topology_type', 'OSPF'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c2b5fb764d888375_v1_2_10').validate(obj) is None


@pytest.mark.networks
def test_get_topology_details(runner, cli, auth_options):
    vlan_details = runner.invoke(cli, [*auth_options, 'networks', 'get-vlan-details'])
    vlan_details = mydict_data_factory('', loads(vlan_details.output))

    result = runner.invoke(cli, [*auth_options, 'networks', 'get-topology-details', '--vlan_id', vlan_details.response[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b9b48ac8463a8aba_v1_2_10').validate(obj) is None


@pytest.mark.networks
def test_get_overall_network_health(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'networks', 'get-overall-network-health'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ca91da84401abba1_v1_2_10').validate(obj) is None

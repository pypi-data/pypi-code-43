import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.path_trace
def test_initiate_a_new_pathtrace(runner, cli, auth_options):
    discoveries = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries = mydict_data_factory('', loads(discoveries.output)).response

    ipAddressLists = [list(set(discovery.ipAddressList.split('-'))) if discovery.ipAddressList else set()
                      for discovery in discoveries]
    ipAddressList = list(set([ip for iplist in ipAddressLists for ip in iplist]))
    ipAddressList.sort()

    result = runner.invoke(cli, [*auth_options, 'path-trace', 'initiate-a-new-pathtrace', '--destip', ipAddressList[-1] if len(ipAddressList) > 0 else "10.20.10.1",
                                 '--sourceip', ipAddressList[0] if len(ipAddressList) > 0 else "10.20.10.1"])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a395fae644ca899c_v1_2_10').validate(obj) is None


@pytest.mark.path_trace
def test_deletes_pathtrace_by_id(runner, cli, auth_options):
    discoveries = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries = mydict_data_factory('', loads(discoveries.output)).response

    ipAddressLists = [list(set(discovery.ipAddressList.split('-'))) if discovery.ipAddressList else set()
                      for discovery in discoveries]
    ipAddressList = list(set([ip for iplist in ipAddressLists for ip in iplist]))
    ipAddressList.sort()

    previous_pathtraces_summary = runner.invoke(cli, [*auth_options, 'path-trace', 'retrives-all-previous-pathtraces-summary', '--source_ip', ipAddressList[0] if len(ipAddressList) > 0 else "10.20.10.1"])
    assert not previous_pathtraces_summary.exception
    obj_pps = loads(previous_pathtraces_summary.output)
    assert json_schema_validate('jsd_55bc3bf94e38b6ff_v1_2_10').validate(obj_pps) is None
    previous_pathtraces_summary = mydict_data_factory('', obj_pps)

    result = runner.invoke(cli, [*auth_options, 'path-trace', 'deletes-pathtrace-by-id', '--flow_analysis_id', previous_pathtraces_summary.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8a9d2b76443b914e_v1_2_10').validate(obj) is None


@pytest.mark.path_trace
def test_retrieves_previous_pathtrace(runner, cli, auth_options):
    discoveries = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries = mydict_data_factory('', loads(discoveries.output)).response

    ipAddressLists = [list(set(discovery.ipAddressList.split('-'))) if discovery.ipAddressList else set()
                      for discovery in discoveries]
    ipAddressList = list(set([ip for iplist in ipAddressLists for ip in iplist]))
    ipAddressList.sort()

    initiate_a_new_pathtrace = runner.invoke(cli, [*auth_options, 'path-trace', 'initiate-a-new-pathtrace', '--destip', ipAddressList[-1] if len(ipAddressList) > 0 else "10.20.10.1",
                                                   '--sourceip', ipAddressList[0] if len(ipAddressList) > 0 else "10.20.10.1"])
    initiate_a_new_pathtrace = mydict_data_factory('', loads(initiate_a_new_pathtrace.output))

    result = runner.invoke(cli, [*auth_options, 'path-trace', 'retrieves-previous-pathtrace', '--flow_analysis_id', initiate_a_new_pathtrace.response.flowAnalysisId])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7ab9a8bd4f3b86a4_v1_2_10').validate(obj) is None

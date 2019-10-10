import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
import time
from functools import reduce


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.network_discovery
def test_delete_all_discovery(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-all-discovery'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_db8e09234a988bab_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_cli_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-cli-credentials',
                                 '--payload', dumps([{"username": "test_user_devnet", "password": "NO!$DATA!$"}])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_948ea8194348bc0b_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_netconf_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-netconf-credentials',
                                 '--payload', dumps([{"netconfPort": '65533'}])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_17929bc7465bb564_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_snmp_write_community(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-snmp-write-community',
                                 '--payload', dumps([{"writeCommunity": "NO!$DATA!$", "description": "created snmpv2"}])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_6bacb8d14639bdc7_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_snmp_read_community(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-snmp-read-community',
                                 '--payload', dumps([{
                                     "readCommunity": "NO!$DATA!$",
                                     "description": "created snmpv2"
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7aa3da9d4e098ef2_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_http_write_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-http-write-credentials',
                                 '--payload', dumps([{
                                     "username": "test_user_devnet",
                                     "password": "W.~&KV9ha",
                                     "port": 8080
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4d9ca8e2431a8a24_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_http_read_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-http-read-credentials',
                                 '--payload', dumps([{
                                     "username": "test_user_devnet",
                                     "password": "W.~&KV9ha",
                                     "port": 8080
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_bf859ac64a0ba19c_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_update_snmp_properties(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-update-snmp-properties',
                                 '--payload', dumps([{
                                     "intValue": 1,
                                     "systemPropertyName": "version"
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a5ac99774c6bb541_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_create_snmpv3_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'create-snmpv3-credentials',
                                 '--payload', dumps([{
                                     "snmpMode": "NOAUTHNOPRIV",
                                     "username": "test_user_devnet"
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_979688084b7ba60d_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_credential_sub_type_by_credential_id(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'CLI'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-credential-sub-type-by-credential-id', '--id', global_credentials.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_58a3699e489b9529_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_snmp_properties(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-snmp-properties'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_44974ba5435a801d_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_start_discovery(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'CLI'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))
    credentialIdList = [['--globalcredentialidlist', '"{}"'.format(x.id)] for x in global_credentials.response]
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'start-discovery',
                                 '--cdplevel', 16,
                                 '--discoverytype', 'CDP',
                                 *reduce(lambda a, b: a + b, credentialIdList[0:5]),
                                 '--ipaddresslist', '10.10.22.22',
                                 '--name', 'start_discovery_test',
                                 '--netconfport', '65535',
                                 '--protocolorder', 'ssh'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_55b439dc4239b140_v1_2_10').validate(obj) is None
    time.sleep(10)


@pytest.mark.network_discovery
def test_get_count_of_all_discovery_jobs(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-count-of-all-discovery-jobs'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_069d9823451b892d_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_discoveries_by_range(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_33b799d04d0a8907_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_network_devices_from_discovery(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-network-devices-from-discovery',
                                 '--id', discoveries_by_range.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_3d9b99c343398a27_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_discovery_by_id(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discovery-by-id', '--id', discoveries_by_range.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_63bb88b74f59aa17_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_list_of_discoveries_by_discovery_id(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-list-of-discoveries-by-discovery-id', '--id', discoveries_by_range.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_99872a134d0a9fb4_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_discovery_jobs_by_ip(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discovery-jobs-by-ip', '--ip_address', discoveries_by_range.response[0].ipAddressList.split('-')[0]])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a4967be64dfaaa1a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_discovered_devices_by_range(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    filtered_discoveries = discoveries_by_range.response
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discovered-devices-by-range',
                                 '--id', filtered_discoveries[0].id,
                                 '--records_to_return', 3,
                                 '--start_index', 1])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a6b798ab4acaa34e_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_devices_discovered_by_id(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-devices-discovered-by-id', '--id', discoveries_by_range.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a6965b454c9a8663_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_global_credentials(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'CLI'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ff816b8e435897eb_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_get_discovered_network_devices_by_discovery_id(runner, cli, auth_options):
    discoveries_by_range = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries_by_range = mydict_data_factory('', loads(discoveries_by_range.output))
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discovered-network-devices-by-discovery-id',
                                 '--id', discoveries_by_range.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f6ac994f451ba011_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_discovery_by_specified_range(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-discovery-by-specified-range', '--records_to_delete', 3, '--start_index', 800])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c1ba9a424c08a01b_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_netconf_credentials(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'NETCONF'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))
    credentials = global_credentials.response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-netconf-credentials', '--id', list(filter(lambda x: x.netconfPort == '65533', credentials))[0].id, '--netconfport', '65532'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c5acd9fa4c1a8abc_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_global_credentials(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'NETCONF'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))
    credentials = global_credentials.response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-global-credentials',
                                 '--global_credential_id', list(filter(lambda x: x.netconfPort == '65532', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_709fda3c42b8877a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_netconf(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'NETCONF'])
    credentials = mydict_data_factory('', loads(global_credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id',
                                 '--global_credential_id', list(filter(lambda x: x.netconfPort == '65532', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_snmp_write_community(runner, cli, auth_options):
    time.sleep(20)
    sub_type = "SNMPV2_WRITE_COMMUNITY"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-snmp-write-community', '--description', 'created snmpv2_write', '--id', list(filter(lambda x: x.description == 'created snmpv2', credentials))[0].id, '--writecommunity', 'NO!$DATA!$'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_10b06a6a4f7bb3cb_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_snmp_read_community(runner, cli, auth_options):
    time.sleep(20)
    sub_type = "SNMPV2_READ_COMMUNITY"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response
    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-snmp-read-community', '--description', 'created snmpv2_read', '--id', list(filter(lambda x: x.description == 'created snmpv2', credentials))[0].id, '--readcommunity', 'NO!$DATA!$'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_47a1b84b4e1b8044_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_cli_credentials(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'CLI'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))
    credentials = global_credentials.response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-cli-credentials', '--description', 'test: user devnet credentials', '--id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id, '--password', 'NO!$DATA!$', '--username', 'test_user_devnet'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_fba0d80747eb82e8_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_snmp_write(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "SNMPV2_WRITE_COMMUNITY"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.description == 'created snmpv2_write', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_snmp_read(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "SNMPV2_READ_COMMUNITY"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.description == 'created snmpv2_read', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_cli(runner, cli, auth_options):
    global_credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', 'CLI'])
    global_credentials = mydict_data_factory('', loads(global_credentials.output))
    credentials = global_credentials.response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_http_write_credentials(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "HTTP_WRITE"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-http-write-credentials', '--description', 'created http_write', '--id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id, '--password', 'W.~&KV9ha', '--port', 8080, '--username', 'test_user_devnet'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_b68a6bd8473a9a25_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_http_read_credential(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "HTTP_READ"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-http-read-credential', '--description', 'created http_write', '--id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id, '--password', 'W.~&KV9ha', '--port', 8080, '--username', 'test_user_devnet'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_89b36b4649999d81_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_update_snmpv3_credentials(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "SNMPV3"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'update-snmpv3-credentials', '--description', 'created snmpv3', '--id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id, '--snmpmode', 'NOAUTHNOPRIV', '--username', 'test_user_devnet'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_1da5ebdd434aacfe_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_http_write(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "HTTP_WRITE"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_http_read(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "HTTP_READ"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_global_credentials_by_id_snmpv3(runner, cli, auth_options):
    time.sleep(10)
    sub_type = "SNMPV3"
    credentials = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-global-credentials', '--credential_sub_type', sub_type])
    credentials = mydict_data_factory('', loads(credentials.output)).response

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-global-credentials-by-id', '--global_credential_id', list(filter(lambda x: x.username == 'test_user_devnet', credentials))[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5ac590c4ca9975a_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_updates_discovery_by_id_active(runner, cli, auth_options):
    discovery = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discovery = mydict_data_factory('', loads(discovery.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'updates-discovery-by-id', '--discoverystatus', discovery.discoveryStatus, '--id', discovery.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9788b8fc4418831d_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_updates_discovery_by_id_inactive(runner, cli, auth_options):
    discovery = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discovery = mydict_data_factory('', loads(discovery.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'updates-discovery-by-id', '--discoverystatus', discovery.discoveryStatus, '--id', discovery.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9788b8fc4418831d_v1_2_10').validate(obj) is None


@pytest.mark.network_discovery
def test_delete_discovery_by_id(runner, cli, auth_options):
    time.sleep(10)
    discoveries = runner.invoke(cli, [*auth_options, 'network-discovery', 'get-discoveries-by-range', '--records_to_return', 10, '--start_index', 1])
    discoveries = mydict_data_factory('', loads(discoveries.output)).response
    discovery_to_delete = list(filter(
        lambda x: x.ipAddressList == '10.10.22.22' and x.name == 'start_discovery_test', discoveries
    ))

    result = runner.invoke(cli, [*auth_options, 'network-discovery', 'delete-discovery-by-id', '--id', discovery_to_delete[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4c8cab5f435a80f4_v1_2_10').validate(obj) is None

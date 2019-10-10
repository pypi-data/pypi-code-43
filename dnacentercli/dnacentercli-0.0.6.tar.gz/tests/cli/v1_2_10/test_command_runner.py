import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.command_runner
def test_get_all_keywords_of_clis_accepted(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'command-runner', 'get-all-keywords-of-clis-accepted'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_33bb2b9d40199e14_v1_2_10').validate(obj) is None


@pytest.mark.command_runner
def test_run_read_only_commands_on_devices(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'command-runner', 'run-read-only-commands-on-devices', '--commands', 'show', '--deviceuuids', device_list.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d6b8ca774739adf4_v1_2_10').validate(obj) is None

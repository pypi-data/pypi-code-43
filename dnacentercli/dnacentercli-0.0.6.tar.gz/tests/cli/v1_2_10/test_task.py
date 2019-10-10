import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.task
def test_get_tasks(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'task', 'get-tasks'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_e78bb8a2449b9eed_v1_2_10').validate(obj) is None


@pytest.mark.task
def test_get_task_tree(runner, cli, auth_options):
    tasks = runner.invoke(cli, [*auth_options, 'task', 'get-tasks'])
    tasks = mydict_data_factory('', loads(tasks.output))

    result = runner.invoke(cli, [*auth_options, 'task', 'get-task-tree', '--task_id', tasks.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f5a269c44f2a95fa_v1_2_10').validate(obj) is None


@pytest.mark.task
def test_get_task_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'task', 'get-task-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_26b44ab04649a183_v1_2_10').validate(obj) is None


@pytest.mark.task
def test_get_task_by_id(runner, cli, auth_options):
    tasks = runner.invoke(cli, [*auth_options, 'task', 'get-tasks'])
    tasks = mydict_data_factory('', loads(tasks.output))

    result = runner.invoke(cli, [*auth_options, 'task', 'get-task-by-id', '--task_id', tasks.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a1a9387346ba92b1_v1_2_10').validate(obj) is None


@pytest.mark.task
def test_get_task_by_operationid(runner, cli, auth_options):
    tasks = runner.invoke(cli, [*auth_options, 'task', 'get-tasks'])
    tasks = mydict_data_factory('', loads(tasks.output)).response
    filtered_tasks = list(filter(lambda x: x.operationIdList is not None, tasks))
    try:
        result = runner.invoke(cli, [*auth_options, 'task', 'get-task-by-operationid', '--limit', 1, '--offset', 0, '--operation_id', filtered_tasks[0].operationIdList[0]])
        assert not result.exception
        if result.output.strip():
            obj = loads(result.output)
            assert json_schema_validate('jsd_e487f8d3481b94f2_v1_2_10').validate(obj) is None
    except Exception:
        print('\nNot able to find valid operationid\n')
        pass

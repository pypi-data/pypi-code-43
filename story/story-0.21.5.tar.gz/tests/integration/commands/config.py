# -*- coding: utf-8 -*-
from pytest import mark


@mark.parametrize('get_result', [
    {},
    {'service1': {'a': 'b'}, 'c': 'd', 'service2': {'e': 'f'}}
])
def test_list(runner, patch, init_sample_app_in_cwd, get_result):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.config import list_command

        patch.object(api.Config, 'get', return_value=get_result)

        result = runner.run(list_command, exit_code=0)

    api.Config.get.assert_called_with('my_app')

    if get_result:
        assert """
        Storyscript variables:
c:  d

Service variables:
service1
  a:  b
service2
  e:  f
""".strip() in result.stdout
    else:
        assert 'No configuration set yet' in result.stdout
        assert 'story config set key=value' in result.stdout
        assert 'story config set service.key=value' in result.stdout


@mark.parametrize('message', ['my message', None])
def test_set(runner, patch, init_sample_app_in_cwd, message):
    args = ['a=b', 'service1.c=d', 'd=f', 'service2.g=h', 'service1.i=j']

    if message:
        args.append('-m')
        args.append(message)

    expected_variables = {
        'A': 'b',
        'D': 'f',
        'service1': {
            'C': 'd',
            'I': 'j'
        },
        'service2': {
            'G': 'h',
            'old_service_var': 'old_val'
        },
        'old_ss_var': 'secret***'
    }

    old_vars = {
        'old_ss_var': 'secret***',
        'service2': {
            'old_service_var': 'old_val'
        }
    }

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.config import set_command

        patch.object(api.Config, 'get', return_value=old_vars)
        patch.object(api.Config, 'set',
                     return_value={'id': 'super_version_number'})

        result = runner.run(set_command, args=args, exit_code=0)

    api.Config.get.assert_called_with(app='my_app')
    api.Config.set.assert_called_with(config=expected_variables,
                                      app='my_app', message=message)

    assert 'Deployed new release' in result.stdout
    assert 'super_version_number' in result.stdout


def test_set_invalid_pair(runner, patch, init_sample_app_in_cwd):
    args = ['ab', 'a=b']

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.config import set_command

        patch.object(api.Config, 'get', return_value={})

        result = runner.run(set_command, args=args, exit_code=1)

    assert 'Config variables must be of the form name=value' in result.stdout
    assert 'Got unexpected pair "ab"' in result.stdout


@mark.parametrize('conf_key_name,get_return_value,stdout_asserts', [
    (
        'service_1',
        {
            'service_1': {
                'a': 'b',
                'c': 'd'
            }
        },
        [
            'A:  b',
            'C:  d'
        ]
    ),
    (
        'service_1.a',
        {
            'service_1': {
                'A': 'b'
            }
        },
        [
            'A:  b'
        ]
    ),
    (
        'service_1',
        {
            'SERVICE_1': {
                'A': 'b'
            }
        },
        [
            'A:  b'
        ]
    ),
    (
        'service_1.a',
        {},
        None
    ),
    (
        'key_1',
        {
            'key_1': 'val_1'
        },
        [
            'KEY_1:  val_1'
        ]
    ),
])
def test_get_for_service(runner, patch, init_sample_app_in_cwd,
                         get_return_value, stdout_asserts, conf_key_name):
    args = [conf_key_name]

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.config import get

        patch.object(api.Config, 'get', return_value=get_return_value)

        result = runner.run(get, args=args, exit_code=0)

    api.Config.get.assert_called_with(app='my_app')

    assert 'Fetching config for my_app' in result.stdout

    if stdout_asserts is None:
        assert f'No variable named "{conf_key_name}"'
    else:
        for line in stdout_asserts:
            assert line in result.stdout

# -*- coding: utf-8 -*-
import os

import click_completion

from pytest import mark

from story.commands import completion


@mark.parametrize('insensitive', [True, False])
@mark.parametrize('shell', ['bash', 'fish', 'zsh', 'powershell', None])
@mark.parametrize('install', [True, False])
@mark.parametrize('path', ['my_completion_file_path', None])
def test_completion(runner, patch, insensitive, shell, install, path):
    patch.object(click_completion.core, 'get_code',
                 return_value='super_cool_completion_code')

    patch.object(click_completion.core, 'install',
                 return_value=(shell, path))

    args = []
    if shell:
        args.append(shell)

    if path:
        args.append('--path')
        args.append(path)

    if install:
        args.append('--install')

    expected_extra_env = {}

    if insensitive:
        args.append('-i')
        expected_extra_env[
            '_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'] = 'ON'

    with runner.runner.isolated_filesystem():
        result = runner.run(completion.completion, args=args, exit_code=0)

    if install:
        click_completion.core.install.assert_called_with(
            shell=shell, path=path, append=True,
            extra_env=expected_extra_env)

        click_completion.core.get_code.assert_not_called()

        assert f'{shell} completion installed in {path}' in result.output
    else:
        click_completion.core.get_code.assert_called_with(
            shell, extra_env=expected_extra_env)

        click_completion.core.install.assert_not_called()
        assert 'super_cool_completion_code' in result.output


def test_custom_startswith():
    assert completion.custom_startswith('full_string', 'full') is True
    assert completion.custom_startswith('full_string', 'not_full') is False


def test_custom_startswith_insensitive():
    os.environ['_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'] = 'ON'

    assert completion.custom_startswith('full_string', 'full') is True
    assert completion.custom_startswith('full_string', 'FULL') is True
    assert completion.custom_startswith('full_string', 'fULl') is True
    assert completion.custom_startswith('full_string', 'not_full') is False
    assert completion.custom_startswith('full_string', 'NOT_full') is False

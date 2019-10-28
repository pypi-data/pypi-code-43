# -*- coding: utf-8 -*-
import json
import os

import click

from pytest import mark

from story import cli

from storyscript.App import App
from storyscript.exceptions import StoryError


@mark.parametrize('mock_tree_as_none', [True, False])
@mark.parametrize('no_stories_found', [True, False])
@mark.parametrize('debug', [True, False])
def test_test(runner, patch, init_sample_app_in_cwd, mock_tree_as_none,
              no_stories_found, debug):
    expected_exit_code = 0
    compile_app_result = {
        'stories': {
            'a1.story': {},
            'a2.story': {}
        }
    }

    args = []
    if debug:
        args.append('--debug')

    if no_stories_found:
        compile_app_result['stories'] = {}
        expected_exit_code = 1

    if mock_tree_as_none:
        compile_app_result = None
        expected_exit_code = 1

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        from story.commands import test
        patch.object(test, 'compile_app', return_value=compile_app_result)

        result = runner.run(test.test, args=args, exit_code=expected_exit_code)

    test.compile_app.assert_called_with('my_app', debug)

    if mock_tree_as_none:
        assert result.stdout == ''
    elif no_stories_found:
        assert 'No stories found' in result.stdout
    else:
        assert 'Looking good!' in result.stdout
        assert 'a1.story' in result.stdout
        assert 'a2.story' in result.stdout


@mark.parametrize('force_compilation_error,compilation_exc', [
    (True, StoryError('E100', 'a.story', path='foo')),
    (True, BaseException('oh no!')),
    (False, None)
])
@mark.parametrize('nested_dir', [True, False])
def test_compile_app(runner, patch, init_sample_app_in_cwd,
                     pre_init_cli_runner, nested_dir,
                     force_compilation_error, compilation_exc):
    app_name_for_analytics = 'my_special_app'

    patch.object(cli, 'get_asyncy_yaml', return_value='asyncy_yml_content')
    patch.object(cli, 'track')

    patch.object(click, 'echo')

    if force_compilation_error:
        patch.object(App, 'compile',
                     side_effect=compilation_exc)

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        actual_project_root = os.getcwd()
        pre_init_cli_runner()
        from story.commands import test

        # nested_dir is used to specifically ensure that when compile_app
        # is executed in a sub directory under the main project, all stories
        # in the project are compiled, and not just the ones that were
        # in that sub directory.
        if nested_dir:
            os.chdir(f'{os.getcwd()}/src/b')

        actual_compilation_result = test.compile_app(app_name_for_analytics,
                                                     False)

        if not force_compilation_error:
            os.chdir(actual_project_root)
            expected_compilation_result = json.loads(App.compile(os.getcwd()))
            expected_compilation_result['yaml'] = 'asyncy_yml_content'

    # Ugly assert, I know. Can't help it since we're not running this via
    # the runner.
    assert 'Compiling Stories' in click.echo.mock_calls[0][1][0]

    if force_compilation_error:
        assert actual_compilation_result is None
        assert 'Failed to compile project' in click.echo.mock_calls[1][1][0]
        err_line = click.echo.mock_calls[2][1][0]
        if isinstance(compilation_exc, StoryError):
            assert 'Please report at ' \
                   'https://github.com/storyscript' \
                   '/storyscript/issues' in err_line
        else:
            assert str(compilation_exc) in err_line
    else:
        assert actual_compilation_result == expected_compilation_result

    cli.track.assert_called_with('App Compiled', {
        'App name': app_name_for_analytics,
        'Result': 'Failed' if force_compilation_error else 'Success',
        'Stories': 0 if force_compilation_error else 2
    })

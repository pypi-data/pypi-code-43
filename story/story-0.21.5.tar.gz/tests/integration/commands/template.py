# -*- coding: utf-8 -*-
import pkgutil

from pytest import mark

from story import cli
from story.commands.template import template


def test_write_choices(runner):
    with runner.runner.isolated_filesystem():
        result = runner.run(template, exit_code=1)
    assert 'Please specify a template' in result.output
    assert 'Run $ story template :template_name:' in result.output


@mark.parametrize('story_name', ['http', 'function', 'if',
                                 'loop', 'slack-bot'])
@mark.parametrize('write_to_file', [True, False])
@mark.parametrize('app_name', [None, 'my_app'])
def test_write_a_story(runner, story_name, patch, write_to_file, app_name):
    patch.object(cli, 'track')
    patch.object(cli, 'get_app_name_from_yml', return_value=app_name)

    file_content = None

    with runner.runner.isolated_filesystem():
        if write_to_file:
            result = runner.run(template, exit_code=0,
                                args=[story_name, 'a.story'])

            with open('a.story', 'r') as f:
                file_content = f.read()

        else:
            result = runner.run(template, exit_code=0, args=[story_name])

    data = pkgutil.get_data('story', f'stories/{story_name}.story')

    expected_output = data.decode('utf-8') + '\n'

    if write_to_file:
        expected_output = '$ cat a.story\n' + expected_output

        assert file_content == data.decode('utf-8')

    assert expected_output == result.output

    cli.track.assert_called_with('App Bootstrapped',
                                 {
                                     'App name': app_name or 'Not created yet',
                                     'Template used': story_name
                                 })

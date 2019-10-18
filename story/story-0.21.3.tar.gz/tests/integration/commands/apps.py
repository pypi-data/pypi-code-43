# -*- coding: utf-8 -*-
import os
from unittest import mock

import click

from pytest import mark

from story import api, awesome, cli
from story.helpers import datetime


def test_list(runner, patch, init_sample_app_in_cwd):
    patch.object(datetime, 'parse_psql_date_str', side_effect=[
        'my_app_1_parsed_date',
        'my_app_2_parsed_date'
    ])

    patch.object(datetime, 'reltime', side_effect=[
        'my_app_1_reltime',
        'my_app_2_reltime',
    ])

    ts_app_1 = '2019-06-26T10:31:22.499142+00:00'
    ts_app_2 = '2018-12-17T10:19:56.659736+00:00'

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.apps import apps
        patch.object(api.Apps, 'list',
                     return_value=[
                         {
                             'name': 'my_app_1',
                             'timestamp': ts_app_1,
                             'maintenance': False
                         },
                         {
                             'name': 'my_app_2',
                             'timestamp': ts_app_2,
                             'maintenance': True
                         },
                     ]
                     )

        args = ['list']
        result = runner.run(apps, args=args)

    expected_output = """
   NAME         STATE            CREATED     
============================================
my_app_1   running          my_app_1_reltime
my_app_2   in maintenance   my_app_2_reltime
    """  # noqa (because there's a trailing whitespace in the header)

    assert result.stdout.strip() == expected_output.strip()

    assert datetime.reltime.mock_calls == [
        mock.call('my_app_1_parsed_date'),
        mock.call('my_app_2_parsed_date')
    ]

    assert datetime.parse_psql_date_str.mock_calls == [
        mock.call(ts_app_1),
        mock.call(ts_app_2)
    ]


def test_list_no_apps(runner, patch, init_sample_app_in_cwd):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.apps import apps
        patch.object(api.Apps, 'list', return_value=[])

        args = ['list']
        result = runner.run(apps, args=args)

    assert 'No application found' in result.stdout
    assert 'story apps create' in result.stdout


def test_do_open(runner, init_sample_app_in_cwd, patch):
    patch.object(click, 'launch')
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story.commands.apps import do_open

        result = runner.run(do_open)

    app_url = 'https://my_app.storyscriptapp.com/'
    click.launch.assert_called_with(app_url)
    assert app_url in result.stdout


@mark.parametrize('isatty', [True, False])
def test_url(patch, runner, init_sample_app_in_cwd, isatty):
    patch.object(click, 'launch')

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story.commands import apps
        patch.object(apps, '_isatty', return_value=isatty)

        result = runner.run(apps.url)

    app_url = 'https://my_app.storyscriptapp.com/'

    if isatty:
        app_url += '\n'

    assert app_url == result.stdout


@mark.parametrize('all_apps', [True, False])
@mark.parametrize('yes_to_all', [True, False])
@mark.parametrize('app_name', [None, 'my_secret_app'])
def test_destroy(patch, runner, init_sample_app_in_cwd, all_apps,
                 yes_to_all, app_name):
    if all_apps and app_name:  # Invalid combination.
        return

    patch.object(api.Apps, 'destroy')
    if all_apps:
        patch.object(api.Apps, 'list', return_value=[
            {'name': 'my_app_1'},
            {'name': 'my_app_2'},
            {'name': 'my_app_3'},
        ])

    patch.object(cli, 'track')

    args = []

    stdin = 'y\n'

    if all_apps:
        stdin = 'y\ny\ny\n'
        args.append('--all')

    if yes_to_all:
        args.append('--yes')
        stdin = None

    if app_name:
        args.append('-a')
        args.append(app_name)

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story.commands import apps
        result = runner.run(apps.destroy, stdin=stdin, args=args)

    if not app_name:
        app_name = 'my_app'  # The default app name, from the current directory

    if all_apps:
        for i in range(1, 4):
            assert f'Destroying application \'my_app_{i}\'' in result.stdout

        assert api.Apps.destroy.mock_calls == [
            mock.call(app='my_app_1'),
            mock.call(app='my_app_2'),
            mock.call(app='my_app_3'),
        ]

        assert cli.track.mock_calls == [
            mock.call('App Destroyed', {'App name': 'my_app_1'}),
            mock.call('App Destroyed', {'App name': 'my_app_2'}),
            mock.call('App Destroyed', {'App name': 'my_app_3'}),
        ]
    else:
        assert f'Destroying application \'{app_name}\'' in result.stdout
        api.Apps.destroy.assert_called_with(app=app_name)
        cli.track.assert_called_with('App Destroyed', {'App name': app_name})


def test_create_inside_an_existing_project(runner, init_sample_app_in_cwd):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        from story.commands.apps import create
        result = runner.run(create, exit_code=1)

        assert 'There appears to be a Storyscript Cloud project in' \
               f' {os.getcwd()}/story.yml already' in result.stdout


def test_create_with_short_name(runner):
    with runner.runner.isolated_filesystem():
        from story.commands.apps import create
        result = runner.run(create, args=['a'], exit_code=1)

    assert 'The name you specified is too short.' in result.stdout
    assert 'use at least 4 characters' in result.stdout


@mark.parametrize('custom_app_name', [None, 'my_custom_app_name_is_too_cool'])
@mark.parametrize('team', [None, 'my_team_name'])
def test_create(runner, patch, custom_app_name, team):
    args = []

    if custom_app_name:
        app_name = custom_app_name
        args.append(app_name)
    else:
        app_name = 'my_app_name_different_than_default'
        patch.object(awesome, 'new', return_value=app_name)

    if team:
        args.append('--team')
        args.append(team)

    from story.commands import apps
    patch.object(apps, 'create_story_yaml', side_effect=apps.create_story_yaml)
    patch.object(api.Apps, 'create')
    patch.object(cli, 'track')

    with runner.runner.isolated_filesystem():
        result = runner.run(apps.create, args=args, exit_code=0)

        with open('story.yml') as f:
            actual_contents_of_story_yml = f.read()

    assert 'Creating story.yml…' in result.stdout
    assert f'App Name: {app_name}' in result.stdout
    assert f'App URL: https://{app_name}.storyscriptapp.com/' in result.stdout
    assert 'We hope you enjoy your deployment experience' in result.stdout

    assert actual_contents_of_story_yml == f'app_name: {app_name}\n'

    apps.create_story_yaml.assert_called_with(app_name)
    api.Apps.create.assert_called_with(name=app_name, team=team)
    cli.track.assert_called_with('App Created', {'App name': app_name})


def test_init_inside_an_existing_project(runner, init_sample_app_in_cwd):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        from story.commands import apps
        result = runner.run(apps.init, args=['myapp'], exit_code=1)

        assert 'There appears to be a Storyscript Cloud project in' \
               f' {os.getcwd()}/story.yml already' in result.stdout


def test_init(runner, patch):
    app_name = 'myapp'
    patch.object(api.Apps, 'get_uuid_from_hostname')
    from story.commands import apps
    patch.object(apps, 'create_story_yaml', side_effect=apps.create_story_yaml)
    with runner.runner.isolated_filesystem():
        result = runner.run(apps.init, args=[app_name], exit_code=0)
        with open('story.yml') as f:
            actual_contents_of_story_yml = f.read()

    apps.create_story_yaml.assert_called_with(app_name)
    api.Apps.get_uuid_from_hostname.assert_called_with(app_name)

    assert 'Creating story.yml…' in result.stdout
    assert f'App Name: {app_name}' in result.stdout
    assert f'App URL: https://{app_name}.storyscriptapp.com/' in result.stdout
    assert 'We hope you enjoy your deployment experience' in result.stdout

    assert actual_contents_of_story_yml == f'app_name: {app_name}\n'

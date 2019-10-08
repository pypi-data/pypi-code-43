# -*- coding: utf-8 -*-
from unittest import mock

from pytest import mark

from story.helpers import datetime


@mark.parametrize('no_releases', [True, False])
@mark.parametrize('limit', [None, 100, 200])
def test_list(runner, patch, init_sample_app_in_cwd, no_releases, limit):
    if not no_releases:
        patch.object(datetime, 'reltime', side_effect=[
            'reltime_100',
            'reltime_200',
            'reltime_300'
        ])

        patch.object(datetime, 'parse_psql_date_str', side_effect=[
            'parsed_100',
            'parsed_200',
            'parsed_300'
        ])

    args = []
    if limit is not None:
        args.append('-n')
        args.append(limit)

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.releases import list_command

        if no_releases:
            patch.object(api.Releases, 'list', return_value=[])
        else:
            patch.object(api.Releases, 'list', return_value=[
                {
                    'id': 100,
                    'state': 'deployed',
                    'timestamp': 'date_app_100',
                    'message': 'my_deployment_message_100'
                },
                {
                    'id': 300,
                    'state': 'deployed',
                    'timestamp': 'date_app_300',
                    'message': 'my_deployment_message_300'
                },
                {
                    'id': 200,
                    'state': 'deployed',
                    'timestamp': 'date_app_200',
                    'message': 'my_deployment_message_200'
                },
            ])

        result = runner.run(list_command, args=args, exit_code=0)

    if limit is None:
        limit = 20  # The supposed default.

    api.Releases.list.assert_called_with('my_app', limit=limit)

    if no_releases:
        assert 'No releases yet for app my_app' in result.stdout
    else:
        assert """
    VERSION    STATUS      CREATED              MESSAGE         
============================================================
v100      Deployed   reltime_100   my_deployment_message_100
v200      Deployed   reltime_200   my_deployment_message_200
v300      Deployed   reltime_300   my_deployment_message_300
""".strip() in result.stdout  # noqa (because there's a trailing whitespace in the header)

        assert datetime.parse_psql_date_str.mock_calls == [
            mock.call('date_app_100'),
            mock.call('date_app_200'),
            mock.call('date_app_300')
        ]

        assert datetime.reltime.mock_calls == [
            mock.call('parsed_100'),
            mock.call('parsed_200'),
            mock.call('parsed_300')
        ]


@mark.parametrize('version_specified,version_number', [
    (False, None),
    (True, '28'),
    (True, '0'),
    (True, 'v28'),
    (True, 'invalid')
])
def test_rollback(runner, patch, init_sample_app_in_cwd,
                  version_specified, version_number):
    expected_rollback_version = 99
    expected_exit_code = 0

    args = []

    if version_specified:
        expected_rollback_version = version_number

        if expected_rollback_version[0] == 'v':
            expected_rollback_version = expected_rollback_version[1:]

        args.append(version_number)

        if version_number == '0' or version_number == 'invalid':
            expected_exit_code = 1

    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()

        from story import api
        from story.commands.releases import rollback

        if not version_specified:
            patch.object(api.Releases, 'get', return_value=[{'id': 100}])
        else:
            patch.object(api.Releases, 'get',
                         return_value=[{'id': version_number}])

        patch.object(api.Releases, 'rollback',
                     return_value={'id': expected_rollback_version})

        result = runner.run(rollback, exit_code=expected_exit_code, args=args)

    if version_number == 'invalid':
        assert 'Invalid release specified.' in result.stdout
        return

    if version_number is not None and version_number[0] == 'v':
        version_number = version_number[1:]

    if version_specified and int(version_number) <= 0:
        assert 'Unable to rollback a release before v1' in result.stdout
        return

    if not version_specified:
        api.Releases.get.assert_called_with(app='my_app')
        assert 'Getting latest release for app my_app' in result.stdout

    assert f'Rolling back to v{expected_rollback_version}' in result.stdout
    assert 'Deployed new release' in result.stdout

    api.Releases.rollback.assert_called_with(version=expected_rollback_version,
                                             app='my_app')

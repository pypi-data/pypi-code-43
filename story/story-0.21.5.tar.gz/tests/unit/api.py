# -*- coding: utf-8 -*-
import json
import re
from urllib.error import URLError

import click

from pytest import fixture, mark

import requests

from story import api
from story.environment import SS_GRAPHQL


@fixture()
def patch_graphql(patch):
    patch.object(api, 'graphql')
    patch.object(api.Apps, 'get_uuid_from_hostname')


@mark.parametrize('with_api_error', [None, 'RandomError',
                                     'InvalidOrExpiredToken'])
@mark.parametrize('api_throws_an_exception',
                  [
                      None,
                      URLError('my_reason'),
                      requests.RequestException(),
                      KeyboardInterrupt()
                  ])
def test_graphql(runner, patch, with_api_error, api_throws_an_exception):
    if with_api_error and api_throws_an_exception:
        # Invalid combination.
        return

    if api_throws_an_exception:
        patch.object(click, 'get_current_context')
        patch.object(requests, 'post', side_effect=api_throws_an_exception)
    else:
        patch.object(requests, 'post')

    if with_api_error:
        requests.post.return_value.json.return_value = {
            'errors': [
                {
                    'message': with_api_error
                }
            ]
        }

        patch.object(click, 'get_current_context')

    my_query = {'my_query': 'hello_world'}
    variables = {
        'var1': 'val1',
        'var2': 'val2'
    }

    with runner.runner.isolated_filesystem():
        from story import cli

    patch.object(cli, 'get_access_token')
    patch.object(cli, 'reset')

    ret_val = api.graphql(my_query, **variables)

    requests.post.assert_called_with(
        SS_GRAPHQL,
        data=json.dumps({
            'query': my_query,
            'variables': variables
        }),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {cli.get_access_token()}',
        },
        timeout=10
    )

    if with_api_error or api_throws_an_exception:
        click.get_current_context().exit.assert_called_with(1)
        if with_api_error == 'InvalidOrExpiredToken':
            cli.reset.assert_called()
        else:
            cli.reset.assert_not_called()
        assert ret_val is None
    else:
        assert ret_val == requests.post.return_value.json.return_value
        cli.reset.assert_not_called()


app_name = 'my_app'


@fixture()
def assert_simple_graphql_call(patch_graphql, magic):
    def wrapper(method, method_args, query, assert_hostname_call=True,
                args={}, graphql_response=None):

        if graphql_response is not None:
            api.graphql.return_value = graphql_response

        ret_val = method(*method_args)
        actual_query = api.graphql.mock_calls[0][1][0]

        if assert_hostname_call:
            args['app'] = api.Apps.get_uuid_from_hostname.return_value

        assert sanitise_graphql_query(query) == sanitise_graphql_query(
            actual_query)

        api.graphql.assert_called_with(
            actual_query,
            **args
        )

        if assert_hostname_call:
            api.Apps.get_uuid_from_hostname.assert_called_with(app_name)

        return ret_val

    return wrapper


@mark.parametrize('graphql_returned_nothing', [True, False])
def test_config_get(assert_simple_graphql_call, graphql_returned_nothing):
    expected_query = """
    query($app: UUID!){
      allReleases(condition: {appUuid: $app},
                  first: 1, orderBy: ID_DESC){
        nodes{
          config
        }
      }
    }
    """

    mock_res = None

    if graphql_returned_nothing:
        mock_res = {}

    ret_val = assert_simple_graphql_call(method=api.Config.get,
                                         method_args=[app_name],
                                         query=expected_query,
                                         graphql_response=mock_res)

    if graphql_returned_nothing:
        assert ret_val == {}
    else:
        assert ret_val == api.graphql()['data']['allReleases']['nodes'][0][
            'config']


def test_apps_destroy(assert_simple_graphql_call):
    expected_query = """
    mutation ($data: UpdateAppByUuidInput!){
              updateAppByUuid(input: $data){
                app{
                  uuid
                }
              }
            }
    """

    ret_val = assert_simple_graphql_call(
        method=api.Apps.destroy,
        method_args=[app_name],
        assert_hostname_call=False,
        args={
            'data': {
                'uuid': api.Apps.get_uuid_from_hostname(
                    app_name),
                'appPatch': {'deleted': True}
            }
        },
        query=expected_query)
    api.Apps.get_uuid_from_hostname.assert_called_with(app_name)
    assert ret_val is None


def test_apps_list(assert_simple_graphql_call):
    expected_query = """
    query{
              allApps(condition: {deleted: false}, orderBy: NAME_ASC){
                nodes{
                  name
                  timestamp
                  maintenance
                }
              }
            }
    """

    ret_val = assert_simple_graphql_call(
        method=api.Apps.list,
        method_args=[],
        assert_hostname_call=False,
        query=expected_query)

    assert ret_val == api.graphql()['data']['allApps']['nodes']


def sanitise_graphql_query(query: str) -> str:
    query = query.strip()
    query = re.sub(r'[\s]{2,}', ' ', query)
    query = query.replace(' ', '_space_')
    query = query.replace('\n', '_new_line_')
    return query

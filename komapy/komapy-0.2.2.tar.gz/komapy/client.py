"""
KomaPy data fetcher and reader.
"""

import json

import bmaclient
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen

from . import exceptions, processing
from .settings import app_settings

__all__ = [
    'set_api_key',
    'set_access_token',
    'set_api_host',
    'fetch_bma_as_dictionary',
    'fetch_bma_as_dataframe',
    'fetch_url_as_dictionary',
    'fetch_url_as_dataframe',
]


def set_api_key(key):
    """
    Set BMA API key to enable accessing the API.

    :param key: BMA API key.
    :type key: str
    """
    app_settings.api_key = key


def set_access_token(token):
    """
    Set BMA access token to enable accessing the API.

    :param token: BMA API access token.
    :type token: str
    """
    app_settings.access_token = token


def set_timezone(name):
    """
    Set app timezone setting.

    :param name: Time zone name, e.g. Asia/Jakarta.
    :type name: str
    """
    app_settings.time_zone = name


def set_api_host(name):
    """
    Override BMA API default host.

    :param name: Host name or IP address.
    :type name: str
    """
    app_settings.host = name


def fetch_bma_as_dictionary(name, **params):
    """
    Make a request to the BMA API and return data as Python dictionary.

    :param name: BMA API name, e.g. doas, edm, tiltmeter, etc.
    :type name: str
    :param params: BMA field query filtering parameters.
    :type params: dict
    :return: Dictionary of resolved BMA API data.
    :rtype: dict
    """
    api = bmaclient.MonitoringAPI(
        api_key=app_settings.api_key,
        access_token=app_settings.access_token)
    if app_settings.host:
        api.host = app_settings.host

    method = api.get_fetch_method(name)
    if not method:
        raise exceptions.ChartError('Unknown parameter name {}'.format(name))
    return method(**params)


def fetch_bma_as_dataframe(name, **params):
    """
    Make a request to the BMA API and return data as Pandas DataFrame.

    :param name: BMA API name, e.g. doas, edm, tiltmeter, etc.
    :type name: str
    :param params: BMA field query filtering parameters.
    :type params: dict
    :return: :class:`pandas.DataFrame` of resolved BMA API data.
    :rtype: :class:`pandas.DataFrame`
    """
    response = fetch_bma_as_dictionary(name, **params)
    return processing.dataframe_from_dictionary(response)


def fetch_url_as_dictionary(url, **params):
    """
    Make a request to the URL and return data as Python dictionary.

    :param url: URL that returns JSON data.
    :type url: str
    :param params: URL query filtering parameters.
    :type params: dict
    :return: Dictionary of resolved URL content.
    :rtype: dict
    """
    full_query_params = '?{}'.format(urlencode(params)) if params else ''
    full_url_with_params = '{url}{query_params}'.format(
        url=url,
        query_params=full_query_params
    )

    with urlopen(full_url_with_params) as content:
        data = json.loads(content.read().decode('utf-8'))

    return data


def fetch_url_as_dataframe(url, **params):
    """
    Make a request to the URL and return data as Pandas DataFrame.
    
    :param url: URL that returns JSON data.
    :type url: str
    :param params: URL query filtering parameters.
    :type params: dict
    :return: :class:`pandas.DataFrame` of resolved URL content.
    :rtype: :class:`pandas.DataFrame`
    """
    response = fetch_url_as_dictionary(url, **params)
    return processing.dataframe_from_dictionary(response)

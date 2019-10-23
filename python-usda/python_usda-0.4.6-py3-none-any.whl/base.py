#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

BASE_URI = 'http://api.nal.usda.gov/'
"""The base URI for all USDA API endpoints."""


class DataGovApiError(BaseException):
    """
    Base class for all Data.gov API errors
    """


class DataGovApiRateExceededError(DataGovApiError):
    """
    Data.gov API rate limit has been exceeded for this key.
    """

    def __init__(self):
        super().__init__('API rate limit has been exceeded.')


class DataGovInvalidApiKeyError(DataGovApiError):
    """
    Supplied Data.gov API key is invalid.
    """

    def __init__(self):
        super().__init__("A invalid Data.gov API key has been supplied. "
                         "Get one at https://api.data.gov/signup")


def api_request(url, **parameters):
    r"""
    Perform a GET request to an API endpoint.

    :param str url: URL to perform a request to.
    :param \**kwargs: GET parameters to send along with the request.
    :return: Parsed JSON data.
    :rtype: dict or list
    :raises requests.exceptions.HTTPError: If a request has a
       HTTP 4xx or 5xx status code.
    :raises ValueError: If the API responds with an error on a GET parameter.
    :raises DataGovApiRateExceededError: If the API rate limit has been
       exceeded for a given API key.
    :raises DataGovInvalidApiKeyError: If the API key is invalid.
    :raises DataGovApiError: If the API returned any error.
    """
    r = requests.get(url, parameters)
    try:
        data = r.json()
    except ValueError:  # Server did not even return a JSON for the error
        r.raise_for_status()
    # The JSON error data when the API rate limit is exceeded is in a
    # different format than on parameter errors. This will handle both.
    if 'errors' in data:
        err = data['errors']['error'][0]
    elif 'error' in data:  # API rate limit exceeded error format
        err = data['error']
    else:
        return data
    if err.get('parameter') is not None:  # Wrong parameter error
        raise ValueError(
            "API responded with an error on parameter '{0}': {1}".format(
                err['parameter'], err['message']))
    elif err['code'] == "OVER_RATE_LIMIT":
        raise DataGovApiRateExceededError()
    elif err['code'] == "API_KEY_INVALID":
        raise DataGovInvalidApiKeyError()
    else:
        raise DataGovApiError("{0}: {1}".format(err['code'], err['message']))


class DataGovClientBase(object):
    """
    Base class for Data.gov API clients.
    """

    def __init__(self, uri_part, api_key, use_format=True):
        """
        :param str uri_part: First part of the path of an API endpoint.
           Usually an organization name.
           For USDA's APIs, the path is ``ndb/``.
        :param str api_key: Data.gov API key to use for all requests.
        :param bool use_format: Enable or disable Automatic return format
           (JSON/XML) adding to URLs.
        """
        self.uri_part = uri_part
        self.key = api_key
        self.use_format = use_format

    def build_uri(self, uri_action):
        """
        Build a valid URI for a specific action.

        :param uri_action: An action on the client's API.
        :type uri_action: usda.enums.UsdaUriActions
        """
        # TODO: Use urllib.parse
        return ''.join([BASE_URI, self.uri_part, uri_action.value])

    def run_request(self, uri_action, **kwargs):
        """
        Execute a request and return an API response.

        :param uri_action: An action on the client's API.
        :type uri_action: usda.enums.UsdaUriActions
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        kwargs['api_key'] = self.key
        if 'format' not in kwargs and self.use_format:
            kwargs['format'] = 'json'
        return api_request(self.build_uri(uri_action), **kwargs)

"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

import requests
from katena_chain_sdk_py.utils.uri import get_uri
from katena_chain_sdk_py.entity.api.raw_response import RawResponse


class Client:
    """ Client is a requests wrapper to dialog with a JSON API. """

    def __init__(self, api_url: str):
        """ Client constructor. """
        self.api_url = api_url

    def get(self, route: str, query_values: dict = None) -> RawResponse:
        """ Wraps the do_request method to do a GET HTTP request. """
        return self.do_request("GET", route, query_values=query_values)

    def post(self, route: str, body: str = "", query_values: dict = None) -> RawResponse:
        """ Wraps the do_request method to do a POST HTTP request. """
        return self.do_request("POST", route, body=body, query_values=query_values)

    def do_request(self, method: str, route: str, body: str = "", query_values: dict = None) -> RawResponse:
        """ Uses the requests package to call a distant api and returns a response. """
        url = get_uri(self.api_url, [route])
        response = requests.request(method, url, data=body, params=query_values)
        return RawResponse(response.status_code, response.content)

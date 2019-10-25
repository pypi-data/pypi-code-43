"""make http requests without relying on non-core packages"""
# pylint: disable=too-many-arguments
from copy import deepcopy
from http.client import HTTPSConnection
import json
from typing import Dict, Mapping, Tuple

from ..errors import HTTPError


class Connection():
    """simple request handler"""

    def __init__(self, url):
        self.url = url
        self.connection = HTTPSConnection(url)


    def close(self):
        """ close the active connection"""
        self.connection.close()


    def request(
            self,
            method: str,
            endpoint: str,
            body: str = None,
            headers: Mapping[str, str] = None) -> Tuple[Dict, int]:
        """send a request"""
        request_headers = deepcopy(headers)
        if request_headers is None:
            request_headers = {}

        self.connection.request(
            method,
            endpoint,
            body=body,
            headers=request_headers,
        )

        response = self.connection.getresponse()

        # first digit of response code indicates its status (4xx/5xx are failures)
        if int(str(response.status)[:1]) in [4, 5]:
            raise HTTPError(
                "HTTP request failed with status code {}\n{}".format(
                    response.status,
                    response.read(),
                )
            )

        response_raw = response.read()
        response_data = json.loads(response_raw)

        return response_data, response.status


    def get(
            self,
            endpoint: str,
            headers: Mapping[str, str] = None):
        """get request handler"""
        return self.request(
            "GET",
            endpoint,
            body=None,
            headers=headers)


    def post(
            self,
            endpoint: str,
            body: Dict = None,
            headers: Mapping[str, str] = None):
        """post request handler"""
        body_str = json.dumps(body)
        request_headers = {"Content-Type": "application/json"}
        if headers is not None:
            for key, val in headers.items():
                request_headers[key] = val

        return self.request(
            "POST",
            endpoint,
            body=body_str,
            headers=request_headers)

"""Base definition for Hockey clients."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import time
from typing import Any

import requests


class HockeyDerivedClient:
    """Base definition for Hockey clients.

    :param name: The name of the derived client
    :param token: The authentication token
    :param parent_logger: The parent logger that we will use for our own logging
    """

    log: logging.Logger
    token: str

    def __init__(self, name: str, token: str, parent_logger: logging.Logger) -> None:
        self.log = parent_logger.getChild(name)
        self.token = token

    def get(self, url: str, *, retry_count: int = 0) -> requests.Response:
        """Perform a GET request to a url

        :param url: The URL to run the GET on
        :param int retry_count: The number of retries remaining if we got a 202 last time

        :returns: The raw response

        :raises Exception: If the request fails with a non 200 status code
        """
        response = requests.get(url, headers={"X-HockeyAppToken": self.token})

        if response.status_code == 202 and retry_count > 0:
            self.log.info(
                f"202 response. Sleeping for 10 seconds before invoking HockeyApp again..."
            )
            time.sleep(10)
            return self.get(url, retry_count=retry_count - 1)

        if response.status_code != 200:
            raise Exception(f"HockeyApp request failed: {url} Error: {response.text}")

        return response

    def post(self, url: str, *, data: Any) -> requests.Response:
        """Perform a POST request to a url

        :param url: The URL to run the GET on
        :param Any data: The JSON serializable data to send

        :returns: The raw response

        :raises Exception: If the request fails with a non 200 status code
        """
        response = requests.post(url, headers={"X-HockeyAppToken": self.token}, json=data)

        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f"HockeyApp request failed: {url} Error: {response.text}")

        return response

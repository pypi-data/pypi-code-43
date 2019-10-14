"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bundesliga-tippspiel-reminder (btr).

btr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

btr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with btr.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import json
import requests
from base64 import b64encode
from typing import Dict, Any, Optional


def api_request(
        endpoint: str,
        method: str,
        params: Dict[Any, Any],
        api_key: Optional[str] = None
) -> Dict[Any, Any]:
    """
    Sends a request to the API
    :param endpoint: The endpoint to send the request to
    :param method: The HTTP method to use
    :param params: The parameters to use
    :param api_key: The API key to use
    :return: The response
    """
    url = "https://hk-tippspiel.com/api/v2/" + endpoint

    headers = {}  # type: Dict[str, str]
    if api_key is not None:
        encoded = b64encode(api_key.encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": "Basic {}".format(encoded)
        }

    return json.loads(requests.request(
        method,
        url,
        headers=headers,
        json=params,
    ).text)


def api_is_authorized(api_key: Optional[str]) -> bool:
    """
    Checks whether or not an API key is authorized
    :param api_key: The API key to check
    :return: True if authorized, False otherwise
    """
    if api_key is None:
        return False
    else:
        resp = api_request("authorize", "get", {}, api_key)
        return resp["status"] == "ok"

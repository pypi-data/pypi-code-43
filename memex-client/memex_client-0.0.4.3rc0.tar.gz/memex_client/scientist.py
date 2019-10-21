from io import BytesIO
from typing import Any
import os
import urllib.parse
from memex_client.client import BRAINIAC_CLIENT_PASSWORD, BRAINIAC_CLIENT_USERNAME
import cloudpickle
import requests


def login(url, username: str, password: str):
    login_url = "{}/api/login".format(url)
    params = {'username': username, 'password': password}
    res = requests.post(url=login_url, json=params)
    return res


def package(some_class: Any, modelName: str,
            url: str = "http://localhost:4000") -> requests.Response:

    res = login(url, os.environ.get(BRAINIAC_CLIENT_USERNAME),
                os.environ.get(BRAINIAC_CLIENT_PASSWORD))
    cookies = res.headers.get("Set-Cookie")

    file = BytesIO(cloudpickle.dumps(some_class))

    files = {"pkledFile": file}
    params = {"modelName": modelName}
    url = urllib.parse.urljoin(url, "/api/model/upload")
    response = requests.put(url, files=files, data=params, headers={"Cookie": cookies})
    return response


__all__ = ["package"]

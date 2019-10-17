# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Genymotion Cloud SaaS API client
"""

import requests
from requests_toolbelt.utils import dump

import gmsaas

from gmsaas.triggererrors import get_fake_http_instance_state
from gmsaas.saas import authcache
from .sioclient import SIOClient
from ..errors import AuthenticationError, ApiError, InvalidJsonError, InstanceError, UnreachableError, RequestError
from ..logger import LOGGER
from ..model.instanceinfo import InstanceInfo, InstanceState, is_instance_starting, is_instance_stopping
from .api import (
    LOGIN_URL,
    RECIPES_URL,
    INSTANCES_URL,
    get_start_disposable_url,
    get_stop_disposable_url,
    get_instance_details_url,
)


HTTP_FAKE_INSTANCE_STATE = get_fake_http_instance_state()


def _http_call(method, url, **kwargs):
    """
    Perform HTTP call and log around it
    """
    LOGGER.info("Request: %s %s", method.upper(), url)
    try:
        response = requests.request(method, url, **kwargs)
        if response:
            LOGGER.info("Response: %s", response.status_code)
        else:
            # In case of error, request and response (including redirects) are logged.
            # Note: request's body is not logged as it can contain critical information.
            response.request.body = "<hidden>"
            LOGGER.info("Response: %s", dump.dump_all(response).decode("utf-8"))
        return response
    except requests.RequestException as exception:
        # Possible exceptions http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        # Despite the fact many causes can trigger exceptions, error message is oriented for ConnectionError.
        raise RequestError(exception)


class Client:
    """
    Genymotion Cloud SaaS HTTP API client
    """

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.jwt = None

    @staticmethod
    def _get_user_agent():
        """
        Craft User Agent HTTP header
        """
        return "Genymobile {} {}".format(gmsaas.__application__, gmsaas.__version__)

    def _get_authorization(self):
        """
        Craft Authorization HTTP header for user
        """
        token = self._get_jwt()
        return "Bearer {}".format(token)

    def _get_headers(self, authorization_needed=True):
        """
        Craft HTTP headers for request
        """
        headers = {"user-agent": self._get_user_agent()}

        if authorization_needed:
            headers["Authorization"] = self._get_authorization()

        return headers

    def _make_session_api_call(self, api_call):
        response = api_call()
        if response.status_code == 401:
            self._fetch_jwt()
            return api_call()
        return response

    def list_recipes(self):
        """
        List available Recipes for user
        """
        LOGGER.debug("Listing available Recipes")
        response = self._make_session_api_call(lambda: _http_call("get", RECIPES_URL, headers=self._get_headers()))

        if response.status_code == 200:
            try:
                return response.json()
            except:
                raise InvalidJsonError(response.status_code, response.text)
        else:
            raise ApiError(response.status_code, response.text)

        return None

    def get_instances(self):
        """
        Return instances from the platform
        Data returned is a dict, key being the uuid, value being an InstanceInfo object
        """
        LOGGER.debug("Listing Instances")
        response = self._make_session_api_call(lambda: _http_call("get", INSTANCES_URL, headers=self._get_headers()))

        if response.status_code == 200:
            try:
                data = response.json()
                instances = {}
                for item in data:
                    assert "uuid" in item
                    assert "name" in item
                    assert "state" in item
                    instance = InstanceInfo(uuid=item["uuid"], name=item["name"], state=item["state"])
                    instances[instance.uuid] = instance
                return instances
            except:
                raise InvalidJsonError(response.status_code, response.text)
        else:
            raise ApiError(response.status_code, response.text)

        return None

    def _get_jwt(self):
        """
        Get JWT for user
        """
        self.jwt = authcache.get_jwt()
        if not self.jwt:
            self._fetch_jwt()
        return self.jwt

    def _fetch_jwt(self):
        LOGGER.info("Requesting new JWT")
        payload = {"email": self.email, "password": self.password}
        response = _http_call("post", LOGIN_URL, json=payload, headers=self._get_headers(False))
        if response.status_code == 200:
            try:
                self.jwt = response.json()["token"]
                authcache.set_jwt(self.jwt)
            except:
                raise AuthenticationError(response.status_code, response.text)
        else:
            raise AuthenticationError(response.status_code, response.text)

    def _request_instance_state(self, instance_uuid):
        """
        Return instance state via HTTP API
        """
        LOGGER.info("[%s] Request instance details", instance_uuid)

        if HTTP_FAKE_INSTANCE_STATE:
            LOGGER.info("Using fake instance state %s", HTTP_FAKE_INSTANCE_STATE)
            return HTTP_FAKE_INSTANCE_STATE

        url = get_instance_details_url(instance_uuid)
        response = self._make_session_api_call(lambda: _http_call("get", url, json={}, headers=self._get_headers()))

        if response.status_code == 200:
            try:
                return response.json()["state"]
            except:
                raise InvalidJsonError(response.status_code, response.text)
        elif response.status_code == 404:
            LOGGER.info("[%s] Instance not found, considering it as DELETED", instance_uuid)
            return InstanceState.DELETED
        raise ApiError(response.status_code, response.text)

    def login(self):
        """
        Perform a login request
        """
        return self._get_jwt()

    def start_disposable_instance(self, recipe_uuid, instance_name, stop_when_inactive, no_wait):
        """
        Start a new disposable Instance
        """
        LOGGER.debug('Starting new "%s" disposable Instance', instance_name)

        if not no_wait:
            # Pre-check SIO connection, no wait mode don't require it
            with SIOClient(jwt=self._get_jwt()) as sio:
                if sio.exception:
                    raise UnreachableError()

        payload = {"instance_name": instance_name, "stop_when_inactive": stop_when_inactive}
        url = get_start_disposable_url(recipe_uuid)

        response = self._make_session_api_call(
            lambda: _http_call("post", url, json=payload, headers=self._get_headers())
        )
        instance_uuid = None
        if response.status_code == 201:
            try:
                instance_uuid = response.json()["uuid"]
            except:
                raise InvalidJsonError(response.status_code, response.text)
        else:
            raise ApiError(response.status_code, response.text)

        if no_wait:
            return instance_uuid

        with SIOClient(jwt=self._get_jwt()) as sio:
            if sio.exception:
                raise UnreachableError()
            state = sio.wait_for_instance_started(instance_uuid)

        if is_instance_starting(state):
            # Perform an HTTP call to be sure in case Socket.IO server got down,
            # or missed to push one message.
            LOGGER.info("[%s] Instance not started yet, perform HTTP request to confirm", instance_uuid)
            state = self._request_instance_state(instance_uuid)

        if state != InstanceState.ONLINE:
            LOGGER.error("[%s] Instance not started", instance_uuid)
            raise InstanceError(instance_uuid, InstanceState.ONLINE, state)

        LOGGER.info("[%s] Instance started", instance_uuid)
        return instance_uuid

    def stop_disposable_instance(self, instance_uuid, no_wait):
        """
        Stop a running disposable Instance
        """
        LOGGER.debug("[%s] Stopping disposable Instance", instance_uuid)

        if not no_wait:
            # Pre-check SIO connection, no wait mode don't require it
            with SIOClient(jwt=self._get_jwt()) as sio:
                if sio.exception:
                    raise UnreachableError()

        url = get_stop_disposable_url(instance_uuid)
        response = self._make_session_api_call(lambda: _http_call("post", url, json={}, headers=self._get_headers()))

        if response.status_code == 200:
            try:
                response.json()
            except:
                raise InvalidJsonError(response.status_code, response.text)
        else:
            raise ApiError(response.status_code, response.text)

        if no_wait:
            return

        with SIOClient(jwt=self._get_jwt()) as sio:
            if sio.exception:
                raise UnreachableError()
            state = sio.wait_for_instance_stopped(instance_uuid)

        if is_instance_stopping(state):
            # Perform an HTTP call to be sure in case Socket.IO server got down,
            # or missed to push one message.
            LOGGER.info("[%s] Instance not stopped yet, perform HTTP request to confirm", instance_uuid)
            state = self._request_instance_state(instance_uuid)

        if state != InstanceState.DELETED:
            LOGGER.error("[%s] Instance not stopped", instance_uuid)
            raise InstanceError(instance_uuid, InstanceState.DELETED, state)

        LOGGER.info("[%s] Instance stopped", instance_uuid)

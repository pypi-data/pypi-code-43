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
Genymotion Cloud SaaS SocketIO client
"""

import os
from collections import namedtuple
from urllib.parse import urlparse
import socketio
import engineio

from gmsaas.timeout import get_start_timeout, get_stop_timeout, wait_until
from ..triggererrors import trigger_sio_unreachable, get_fake_sio_instance_state, trigger_unrecognized_state
from ..logger import LOGGER, get_logger
from ..model.instanceinfo import InstanceInfo, InstanceState, is_instance_starting, is_instance_stopping


SIO_BASE_URL = os.environ.get("GM_PLATFORM_SIO_BASE_URL", "https://ws.geny.io/cloud")
SIO_QUERY_STRING = "?token=Bearer%20{}"
SIO_FAKE_INSTANCE_STATE = get_fake_sio_instance_state()
SIO_UNRECOGNIZED_INSTANCE_STATE = trigger_unrecognized_state()
SIO_LOGGER = get_logger(logger_name="sio", version=None)

SocketIOUrl = namedtuple("SocketIOUrl", ["base", "path"])


def _get_socketio_url(jwt):
    """
    Return a SocketIOUrl named tuple for SocketIO connection

    Notes:
        SocketIO lib connection method takes two arguments:
            - url: base url (including query string params)
            - socketio_path: which is `socket.io` by default
        From our point of view:
            - url should be `https://ws.geny.io/cloud?token=...`
            - socketio_path: is right by default
        But the lib removes `/cloud` from our base url and so tries to connect to:
        `https://ws.geny.io/socket.io?token=...`.
        To counter that we need to deconstruct our base url in order to set in the lib:
            - url: `https://ws.geny.io?token=...`
            - socketio_path: cloud/socket.io
        This is what this method is doing.
    """
    base_url = urlparse(SIO_BASE_URL)
    sio_base_url = "{}://{}{}".format(base_url.scheme, base_url.netloc, SIO_QUERY_STRING.format(jwt))
    sio_path = base_url.path + "/socket.io"
    return SocketIOUrl(sio_base_url, sio_path)


class SIOConnectionError(Exception):
    """
    Exception that can occur at connection time
    """

    pass


class SIOClient(object):
    """
    Genymotion Cloud SaaS SocketIO client

    Use socket.io python implementation: https://python-socketio.readthedocs.io
    This class is designed to get push notifications about instances state.

    Architecture:
        - Connection:
            Raises SIOConnectionError exception when failed.
        - Subscription:
            Once connected, subscription to `devices-lifecycle` tag is done
        - Events:
            Once subscribed, all events are received and treated.
            All instances state are stored in a dict.
        - Wait conditions:
            Convenient functions are available to wait for a instance to be in particular state

    Usage:
        SIOClient is a context manager, so connection and disconnection is implicit.

        with SIOClient(jwt=jwt) as sio:
            # Don't forget to check exception that can occur during connection
            if sio.exception:
                # Handle connection error
            if not sio.wait_for_...():
                # Handle wait condition error
    """

    def __enter__(self):
        try:
            self._connect()
            if trigger_sio_unreachable():
                raise engineio.exceptions.ConnectionError()
        except:
            LOGGER.exception("Unable to connect SIO")
            self.exception = SIOConnectionError()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._disconnect()

    def __init__(self, jwt):
        self.exception = None
        self.jwt = jwt
        self.client = socketio.Client(logger=SIO_LOGGER, reconnection=False)
        self.client.eio.logger = SIO_LOGGER
        self.instances = dict()
        self.client.on("connect", self._on_connected)
        self.client.on("disconnect", lambda: LOGGER.debug("SIO client disconnected"))
        self.client.on("devices-lifecycle", self._on_instance_changed)

    def _on_connected(self):
        LOGGER.debug("SIO client connected to %s", _get_socketio_url("jwt"))
        self.client.emit(event="subscribe", data={"tags": ["devices-lifecycle"]})

    def _on_instance_changed(self, data):
        try:
            state = data["data"]["instance_state"]
            instance_uuid = data["data"]["instance"]["uuid"]
        except:
            LOGGER.error("Unreadable devices-lifecycle message: %s", data)
            return

        if SIO_UNRECOGNIZED_INSTANCE_STATE:
            if state == InstanceState.BOOTING or state == InstanceState.DELETING:
                state = "UNRECOGNIZED_STATE"

        if state not in InstanceState.__dict__:
            LOGGER.error("Unrecognized instance state %s", state)
            return

        if not self.instances.get(instance_uuid):
            LOGGER.debug("Added instance %s", instance_uuid)
            self.instances[instance_uuid] = InstanceInfo(instance_uuid)
        self.instances[instance_uuid].set_state(state)

    def _get_instance_state(self, instance_uuid):
        if SIO_FAKE_INSTANCE_STATE:
            LOGGER.info("Using fake instance state %s", SIO_FAKE_INSTANCE_STATE)
            return SIO_FAKE_INSTANCE_STATE
        return self.instances.get(instance_uuid, InstanceInfo(instance_uuid)).state

    def _connect(self):
        """
        Connect SocketIO client
        """
        url = _get_socketio_url(self.jwt)
        LOGGER.debug("Starting SIO client to %s", url)

        self.client.connect(url=url.base, socketio_path=url.path)

    def _disconnect(self):
        self.client.disconnect()

    def wait_for_instance_started(self, instance_uuid):
        """
        Return the actual state whether it succeeds or not, the caller needs to check it.
        """
        LOGGER.debug("Waiting for %s started", instance_uuid)
        wait_until(lambda: not is_instance_starting(self._get_instance_state(instance_uuid)), get_start_timeout())
        return self._get_instance_state(instance_uuid)

    def wait_for_instance_stopped(self, instance_uuid):
        """
        Return the actual state whether it succeeds or not, the caller needs to check it.
        """
        LOGGER.debug("Waiting for %s stopped", instance_uuid)
        wait_until(lambda: not is_instance_stopping(self._get_instance_state(instance_uuid)), get_stop_timeout())
        return self._get_instance_state(instance_uuid)

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
GMSaaS Instance data
"""

from ..logger import LOGGER


DEFAULT_ADB_SERIAL = "0.0.0.0"


class InstanceState:
    """
    Possible state for Instances
    Note:
    - DELETED state is not part of the HTTP API but is still sent by push microservice.
    - UNKNOWN state is used internally when no state has been received yet.
    """

    # pylint: disable=too-few-public-methods
    UNKNOWN = "UNKNOWN"
    CREATING = "CREATING"
    OFFLINE = "OFFLINE"
    STARTING = "STARTING"
    BOOTING = "BOOTING"
    ONLINE = "ONLINE"
    SAVING = "SAVING"
    SAVED = "SAVED"
    STOPPING = "STOPPING"
    DELETING = "DELETING"
    DELETED = "DELETED"
    MAINTENANCE = "MAINTENANCE"
    RECYCLED = "RECYCLED"
    ERROR = "ERROR"


class TunnelState:
    """
    Possible states for AdbTunnel
    """

    # pylint: disable=too-few-public-methods
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    PENDING = "PENDING"
    FAILED = "FAILED"
    PORT_BUSY = "PORT_BUSY"


def is_instance_starting(actual_state):
    """
    Return True if instance is neither started nor in failure, False otherwise.
    """
    return actual_state in [
        InstanceState.UNKNOWN,
        InstanceState.CREATING,
        InstanceState.OFFLINE,
        InstanceState.STARTING,
        InstanceState.BOOTING,
    ]


def is_instance_stopping(actual_state):
    """
    Return True if instance is neither stopped nor in failure, False otherwise.
    """
    return actual_state in [
        InstanceState.UNKNOWN,
        InstanceState.STOPPING,
        InstanceState.OFFLINE,
        InstanceState.DELETING,
    ]


def is_adbtunnel_connecting(actual_state):
    """
    Return True if instance is neither connected nor in failure, False otherwise.
    """
    return actual_state in [TunnelState.DISCONNECTED, TunnelState.PENDING]


class InstanceInfo:
    """
    InstanceInfo represents information about one instance
    """

    def __init__(
        # pylint: disable-msg=C0330
        self,
        uuid,
        name="",
        adb_serial=DEFAULT_ADB_SERIAL,
        state=InstanceState.UNKNOWN,
        tunnel_state=TunnelState.DISCONNECTED,
    ):
        self.uuid = uuid
        self.name = name
        self.adb_serial = adb_serial
        self.state = state
        self.tunnel_state = tunnel_state

    def __str__(self):
        return "uuid={}, name={}, state={}, adb_serial={}, tunnel_state={}".format(
            self.uuid, self.name, self.state, self.adb_serial, self.tunnel_state
        )

    def set_state(self, state):
        """
        Update instance state
        """
        LOGGER.debug("[%s] Update instance state from %s to %s", self.uuid, self.state, state)
        self.state = state

    def get_port(self):
        """
        Return port retrieved from ADB Serial, None on failure
        """
        try:
            return [x for x in self.adb_serial.split(":") if x][1]
        except:
            return None

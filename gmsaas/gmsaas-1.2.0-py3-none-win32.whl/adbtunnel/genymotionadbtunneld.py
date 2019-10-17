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
genymotionadbtunneld binary wrapper
"""

import os
import json
import subprocess

import gmsaas
from gmsaas.timeout import get_adbtunnel_connect_timeout, get_adbtunnel_stop_timeout, wait_until
from gmsaas.model.instanceinfo import InstanceInfo, TunnelState, is_adbtunnel_connecting
from gmsaas.model.daemoninfo import AdbTunnelDaemonInfo
from gmsaas.errors import PackageError
from gmsaas.saas.api import CLOUD_BASE_URL

from ..logger import LOGGER


TunnelExitCode = type("TunnelExitCode", (), {"EXIT_OK": 0, "EXIT_NOT_RUNNING": 1})

CHECK_INSTANCE_STATE_INTERVAL = 3


class GenymotionAdbTunneld:
    """
    genymotionadbtunneld representation
    """

    def __init__(self, exec_bin):
        self.exec_bin = exec_bin
        if "GMADBTUNNELD_PATH" in os.environ:
            self.exec_bin = os.environ["GMADBTUNNELD_PATH"]

    def is_ready(self):
        """
        Return True if adbtunnel daemon is found and executable, False otherwise
        """
        return os.path.exists(self.exec_bin) and os.path.isfile(self.exec_bin) and os.access(self.exec_bin, os.X_OK)

    def _exec(self, args):
        cmd = [self.exec_bin]
        cmd.extend(args)
        try:
            subprocess.Popen(cmd)
        except FileNotFoundError:
            raise PackageError()

    def _rpc_call(self, args):
        """
        Sends an RPC call to gmadbtunneld, returns a dict containing the answer
        """
        cmd = [self.exec_bin]
        cmd.extend(args)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise PackageError()
        out = proc.stdout.decode("utf-8")
        return json.loads(out)

    def connect(self, instance_uuid, adb_serial_port=None):
        """
        Connect an Instance to ADB
        """
        LOGGER.info("[%s] Connecting instance to ADB tunnel", instance_uuid)
        args = ["connect", str(instance_uuid)]
        if adb_serial_port:
            LOGGER.info("[%s] Using port %d for instance", instance_uuid, adb_serial_port)
            args.extend(["--adb-serial-port", str(adb_serial_port)])
        self._exec(args)

    def disconnect(self, instance_uuid):
        """
        Disconnect an Instance from ADB
        """
        LOGGER.info("[%s] Connecting instance from ADB tunnel", instance_uuid)
        args = ["disconnect", str(instance_uuid)]
        self._exec(args)

    def stop(self):
        """
        Stop the running genymotionadbtunneld process
        """
        LOGGER.info("Stopping ADB tunnel")
        args = ["stop"]
        self._exec(args)

        if not wait_until(lambda: not self.get_instances(), get_adbtunnel_stop_timeout()):
            LOGGER.error("ADB tunnel still have connected instances")

        LOGGER.debug("ADB tunnel stopped")

    def get_daemon_info(self):
        """
        Get information about gmadbtunneld
        """
        data = self._rpc_call(["getdaemoninfo"])
        if not data:
            # gmadbtunneld is not running, so compatible for sure.
            return AdbTunnelDaemonInfo(gmsaas.__version__, CLOUD_BASE_URL)
        assert "platform_url" in data
        assert "version" in data
        return AdbTunnelDaemonInfo(data["version"], data["platform_url"])

    def get_instances(self):
        """
        Return instances from genymotionadbtunneld
        Data returned is a dict, key being the uuid, value being an InstanceInfo object
        """
        data = self._rpc_call(["getinstances"])
        instances = {}
        if not data:
            return instances
        assert "instances" in data
        items = data["instances"]
        for item in items:
            assert "uuid" in item
            assert "adb_serial" in item
            assert "state" in item
            instance = InstanceInfo(uuid=item["uuid"], adb_serial=item["adb_serial"], tunnel_state=item["state"])
            instances[instance.uuid] = instance
        return instances

    def get_instance(self, instance_uuid):
        """
        Return InstanceInfo for instance_uuid from genymotionadbtunneld
        """
        data = self.get_instances()
        return data.get(instance_uuid, InstanceInfo(uuid=instance_uuid))

    def wait_for_adb_connected(self, instance_uuid):
        """
        Return the actual tunnel state whether it succeeds or not, the caller needs to check it.
        """
        LOGGER.debug("Waiting for %s connected to ADB", instance_uuid)
        wait_until(
            lambda: not is_adbtunnel_connecting(self.get_instance(instance_uuid).tunnel_state),
            get_adbtunnel_connect_timeout(),
            CHECK_INSTANCE_STATE_INTERVAL,
        )
        return self.get_instance(instance_uuid).tunnel_state

    def wait_for_adb_disconnected(self, instance_uuid):
        """
        Return the actual tunnel state whether it succeeds or not, the caller needs to check it.
        """
        LOGGER.debug("Waiting for %s disconnected from ADB", instance_uuid)
        wait_until(
            lambda: self.get_instance(instance_uuid).tunnel_state == TunnelState.DISCONNECTED,
            get_adbtunnel_connect_timeout(),
        )
        return self.get_instance(instance_uuid).tunnel_state

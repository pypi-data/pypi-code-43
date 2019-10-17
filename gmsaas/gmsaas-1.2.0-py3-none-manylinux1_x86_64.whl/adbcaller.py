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
ADB Caller
"""
import os
import platform
from subprocess import check_output, CalledProcessError

from gmsaas.cli.config import SDK_PATH_KEY, get_config_storage
from gmsaas.logger import LOGGER


ADB_EXEC = {"Windows": "adb.exe", "Linux": "adb", "Darwin": "adb"}


class AdbCaller:
    """
    ADB Caller
    """

    def __init__(self):
        storage = get_config_storage()
        sdk_path = storage.get(SDK_PATH_KEY) or ""
        self.exec_bin = os.path.join(sdk_path, "platform-tools", ADB_EXEC[platform.system()])
        LOGGER.info("ADB path: %s", self.exec_bin)

    def is_ready(self):
        """
        Return True if ADB is found and executable, False otherwise
        """
        return os.path.exists(self.exec_bin) and os.path.isfile(self.exec_bin) and os.access(self.exec_bin, os.X_OK)

    def _check_output(self, serial, cmd):
        command = [self.exec_bin, "-s", serial]
        command.extend(cmd)
        try:
            LOGGER.info("Executing %s", command)
            output = check_output(command).decode("utf-8").strip()
        except CalledProcessError as exception:
            LOGGER.warning("AdbCaller process failed: %s", str(exception))
            return None
        return output

    def logcat(self, serial):
        """
        Perform adb logcat, return None in case of failure
        """
        # -d: Dump the log and then exit (don't block)
        return self._check_output(serial, ["logcat", "-d"])

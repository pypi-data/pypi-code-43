#!/usr/bin/env python
# Copyright (c) 2019 Radware LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# @author: Leon Meguira, Radware


from abc import ABCMeta, abstractmethod
from radware.sdk.api import BaseAPI
from radware.sdk.exceptions import DeviceError

MSG_NOT_ACCESSIBLE = 'Device not accessible'
MSG_REBOOT = 'Device Reset'
MSG_REBOOT_STATEFUL = 'Device Restarted and Returned'
MSG_IMG_UPLOAD = 'Image Uploaded Successfully'
MSG_CONFIG_DOWNLOAD = 'Configuration Downloaded Successfully'
MSG_CONFIG_UPLOAD = 'Configuration Uploaded Successfully'


class DeviceInfo(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def device_name(self):
        pass

    @property
    @abstractmethod
    def mac_address(self):
        pass

    @property
    @abstractmethod
    def uptime(self):
        pass

    @property
    @abstractmethod
    def platform_id(self):
        pass

    @property
    @abstractmethod
    def software(self):
        pass


class DeviceOper(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def reboot(self):
        pass

    @abstractmethod
    def reboot_stateful(self, timeout_seconds):
        pass


class DeviceConfig(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def commit_save(self):
        pass

    @abstractmethod
    def revert(self):
        pass


class DeviceManagement(BaseAPI):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def _device_mng_info(self) -> DeviceInfo:
        pass

    @property
    @abstractmethod
    def _device_mng_oper(self) -> DeviceOper:
        pass

    @property
    @abstractmethod
    def _device_mng_config(self) -> DeviceConfig:
        pass

    @abstractmethod
    def is_accessible(self, timeout_seconds, retries):
        pass

    @property
    def device_name(self):
        return self._device_mng_info.device_name

    @property
    def device_mac_address(self):
        return self._device_mng_info.mac_address

    @property
    def device_uptime(self):
        return self._device_mng_info.uptime

    @property
    def device_platform(self):
        return self._device_mng_info.platform_id

    @property
    def device_software(self):
        return self._device_mng_info.software

    def reboot(self):
        return self._device_mng_oper.reboot()

    def reboot_stateful(self, timeout_seconds):
        return self._device_mng_oper.reboot_stateful(timeout_seconds)

    def verify_device_accessible(self, timeout_second=5, retries=1):
        if not self.is_accessible(timeout_second, retries):
            raise DeviceError(None, MSG_NOT_ACCESSIBLE)
        return True



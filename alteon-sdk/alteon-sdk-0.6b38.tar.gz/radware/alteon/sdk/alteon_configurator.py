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


from radware.alteon.api import AlteonDevice
from radware.sdk.configurator import *
import logging

log = logging.getLogger(__name__)


class AlteonConfigurator(DeviceConfigurator, AlteonDevice):
    __metaclass__ = ABCMeta

    def __init__(self, bean_map, alteon_connection):
        AlteonDevice.__init__(self, alteon_connection)
        DeviceConfigurator.__init__(self, bean_map)

    def read(self, parameters: RadwareParametersStruct, validate_required=True, **kw) -> RadwareParametersStruct:
        log.debug(' {0}: {1}, server: {2}, params: {3}, args: {4}'.format(self.__class__.__name__, self.READ.upper(),
                                                                          self.id, parameters, kw))
        prepared_params = self._validate_prepare_parameters(parameters, validate_required)
        return self._read(prepared_params)

    def update(self, parameters: RadwareParametersStruct, dry_run=False, remove_items: RadwareParametersStruct = None,
               **kw) -> str:
        log.debug(' {0}: {1}, server: {2}, dry_run: {4}, params: {3}, remove_items: {5}, args: {6}'.format(
            self.__class__.__name__, self.UPDATE.upper(), self.id, parameters, dry_run, remove_items, kw))
        prepared_params = self._validate_prepare_parameters(parameters)
        if remove_items:
            self._update_remove(remove_items, dry_run=dry_run)
        return self._update(prepared_params, dry_run=dry_run)

    @abstractmethod
    def _read(self, parameters):
        pass

    @abstractmethod
    def _update(self, parameters, dry_run):
        pass

    def _update_remove(self, parameters, dry_run):
        pass

    @property
    def _device_api(self) -> DeviceAPI:
        return self.api

    @property
    def id(self) -> str:
        return self.connection.id



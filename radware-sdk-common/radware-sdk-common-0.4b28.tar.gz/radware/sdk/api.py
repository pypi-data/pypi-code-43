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

from radware.sdk.beans_common import BaseBeanEnum
from radware.sdk.common import get_annotation_class
from abc import ABCMeta, abstractmethod
from radware.sdk.common import RadwareParametersStruct
from typing import Type, get_type_hints


class BaseAPI(object):
    __metaclass__ = ABCMeta

    @classmethod
    def api_function_names(cls):
        func_names = list()
        exclude_func_list = list()
        exclude_func_list.extend(dir(BaseDevice))
        exclude_func_list.extend(dir(BaseAPI))
        exclude_func_list.extend(dir(ConfiguratorAPI))
        for item in dir(cls):
            if not item.startswith('_') and item not in exclude_func_list:
                if callable(getattr(cls, item)):
                    func_names.append(item)
                elif type(getattr(cls, item)) == property:
                    func_names.append(item)
        return func_names

    @staticmethod
    def _dict_keys_translation(src_dict, attrs_dict):
        new_dict = dict()
        for k, v in src_dict.items():
            if k in attrs_dict:
                new_dict.update({attrs_dict[k]: v})
            else:
                new_dict.update({k: v})
        return new_dict


class BaseDeviceConnection(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def connection_details_update(self, **kwargs):
        pass


class BaseDevice(object):
    __metaclass__ = ABCMeta

    def __init__(self, device_connection: BaseDeviceConnection):
        self._connection = device_connection

    @property
    @abstractmethod
    def connection(self):
        pass

    @property
    @abstractmethod
    def api(self):
        pass


class ConfiguratorAPI(object):
    __metaclass__ = ABCMeta

    @staticmethod
    def _enum_to_int(enum_class, value):
        if value:
            if not isinstance(value, BaseBeanEnum):
                return enum_class.value_for_name(value)
            else:
                return value.value

    @classmethod
    def get_parameters_class(cls) -> Type[RadwareParametersStruct]:
        return get_annotation_class(get_type_hints(cls)['parameters_class'])

    def dry_run_delete_procedure(self, diff):
        # overriding configurator may alter diff / return DryRunDeleteProcedure
        pass

    @property
    @abstractmethod
    def id(self):
        pass


class DeviceAPI(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, bean, retries=3):
        pass

    @abstractmethod
    def read_all(self, bean, retries=3):
        pass

    @abstractmethod
    def update(self, bean, retries=3, dry_run=None):
        pass

    @abstractmethod
    def delete(self, bean, retries=3, dry_run=None):
        pass

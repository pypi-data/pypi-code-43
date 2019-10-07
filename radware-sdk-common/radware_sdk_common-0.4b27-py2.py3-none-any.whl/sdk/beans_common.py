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


import logging
import json
import binascii
from enum import Enum
import platform
from abc import ABCMeta
from radware.sdk.exceptions import ArgumentNotExpectedError


log = logging.getLogger(__name__)


def is_py3():
    ver = platform.python_version_tuple()
    return int(ver[0]) >= 3


def remove_empty_dict_key(d):
    new_dict = dict()
    for key, val in d.items():
        if val is not None:
            new_dict.update({key: val})
    return new_dict


class DeviceBean(object):
    __metaclass__ = ABCMeta

    def __str__(self):

        return "class: {0} , attributes: {1} ".format(self.__class__.__name__, remove_empty_dict_key(self.__dict__))

    def to_json_int(self):
        obj = dict()
        obj_idx_names = tuple()
        if hasattr(self, 'get_index_names'):
            obj_idx_names = self.get_index_names()

        for k, v in self.__dict__.items():
            if k not in obj_idx_names and v is not None:
                if isinstance(v, BaseBeanEnum):
                    setattr(self, k, v.name)

        for k, v in self.translate_self().__dict__.items():
            if k not in obj_idx_names and v is not None:
                if isinstance(v, BaseBeanEnum):
                    obj[k] = v.value
                else:
                    obj[k] = v
        _j_dumps = json.dumps(obj)
        return json.loads(_j_dumps)

    def to_json_str(self):
        _j_dumps = json.dumps(self.to_dict_str())
        return json.loads(_j_dumps)

    def to_dict_str(self) -> dict:
        obj = dict()
        for k, v in self.__dict__.items():
            if v is not None and isinstance(v, BaseBeanEnum):
                obj[k] = v.name
            else:
                if v != READ_PROP:
                    obj[k] = v
        return obj

    def translate_json(self, **kwargs):
        return self.get_instance(**kwargs)

    def translate_self(self):
        return self.get_instance(**self.to_dict_str())

    @classmethod
    def get_instance(cls, **kwargs):
        return cls(**kwargs)

    def read(self, client):
        result = client.api.read_no_translation(self)
        return self.get_instance(**result)


class BaseBeanEnum(Enum):

    @classmethod
    def enum(cls, attribute):
        if attribute is None:
            return
        if type(attribute) == cls:
            return attribute
        if type(attribute) != int:
            if attribute in cls.__dict__:
                return cls[attribute]
        else:
            for v in iter(cls):
                if v.value == attribute:
                    return v
        raise ArgumentNotExpectedError(attribute, "enum value: {1} not found in {0}".format(cls, attribute))

    @classmethod
    def value_names(cls):
        name_list = list()
        for attr in dir(cls):
            if not attr.startswith('__'):
                name_list.append(attr)
        return name_list

    @classmethod
    def value_for_name(cls, name):
        return cls[name].value

    @staticmethod
    def is_equal(enum_value, other_value):
        if isinstance(other_value, Enum):
            return enum_value == other_value
        else:
            try:
                return enum_value == enum_value.__class__[other_value]
            except KeyError:
                return False


class BeanUtils(object):

    @staticmethod
    def get_next_available_numeric_idx(current_used_index_list, start_idx=1):
        while 1:
            if start_idx not in current_used_index_list:
                current_used_index_list.append(start_idx)
                return start_idx
            start_idx += 1

    @staticmethod
    def decode_bmp(bmap_str):
        items = []
        bit_str = Decoders.hex_str_bit_str(bmap_str)
        for bit_idx, bit in enumerate(bit_str):
            if bit == '1':
                net_idx = int(bit_idx) + 1
                items.append(net_idx)
        return items

    @staticmethod
    def decode_bmp_sub_one(bmap_str):
        items = []
        bit_str = Decoders.hex_str_bit_str(bmap_str)
        for bit_idx, bit in enumerate(bit_str):
            if bit == '1':
                net_idx = int(bit_idx) + 1
                items.append(net_idx - 1)
        return items


class Decoders(object):
    @staticmethod
    def hex_str_to_ascii(hex_str):
        if is_py3():
            return bytes.fromhex(hex_str.replace(':','')).decode('ascii')
        else:
            return hex_str.replace(':', '').decode("hex")

    @staticmethod
    def hex_str_bit_str(hex_str):
        hex_str = hex_str.replace(':', '')
        byte_data = binascii.unhexlify(hex_str)
        result_str = ''
        for byte_item in byte_data:
            if is_py3():
                result_str += "{:08b}".format(byte_item)
            else:
                result_str += "{:08b}".format(int(byte_item.encode('hex'), 16))
        return result_str


READ_PROP = DeviceBean

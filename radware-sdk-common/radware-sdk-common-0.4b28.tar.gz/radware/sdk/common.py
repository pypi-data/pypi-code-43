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


import os
import platform
from enum import Enum
from radware.sdk.exceptions import *
from radware.sdk.rest_driver import RestSession
from abc import ABCMeta, abstractmethod
from typing_inspect import is_generic_type, get_origin, get_args, is_optional_type, is_classvar
from typing import List, get_type_hints
import logging

log = logging.getLogger(__name__)

RADWARE_PASSWORD_URL = 'http://services.radware.com:80/api/securityupdate/v1/password'


def is_py3():
    ver = platform.python_version_tuple()
    return int(ver[0]) >= 3


def is_annotation_type_list_incl_optional_lookup(value):
    if is_annotation_type_optional(value):
        return is_optional_type_list(value)
    else:
        return is_annotation_type_list(value)


def is_annotation_type_list(value):
    if is_generic_type(value):
        return get_origin(value) == List or get_origin(value) == list


def is_annotation_type_optional(value):
    return is_optional_type(value)


def is_optional_type_list(opt_value):
    union_args = get_args(opt_value)
    if type(union_args) != tuple:
        return False
    else:
        if type(union_args[0]) != tuple:
            return is_annotation_type_list(union_args[0])
        else:
            return is_annotation_type_list(union_args[0][0])


def get_annotation_class(value):
    if is_generic_type(value):
        if is_annotation_type_list(value):
            return get_args(value)[0]
        else:
            raise ArgumentNotExpectedTypeError(value, 'unknown annotation value - class not supported')
    elif is_annotation_type_optional(value):
        union_args = get_args(value)
        opt_classes = get_annotation_class(union_args[0])
        if type(opt_classes) != tuple:
            return opt_classes
        if len(opt_classes) == 1:
            return opt_classes[0]
        elif len(opt_classes) == 2:
            if opt_classes[0] == List:
                return get_annotation_class(opt_classes[1])
            else:
                raise ArgumentNotExpectedTypeError(opt_classes, "unexpected optional annotation value - {0}".format(
                    opt_classes))
    elif is_classvar(value):
        class_args = get_args(value)
        if type(class_args) != tuple:
            return class_args
        else:
            return class_args[0]
    else:
        return value


def recursive_array_sort(arr):
    def _add_type_item(new_type_item):
        if type(new_type_item).__name__ not in type_items_dict:
            type_items_dict.update({type(new_type_item).__name__: [new_type_item]})
        else:
            type_items_dict[type(new_type_item).__name__].append(new_type_item)

    new_array = list()
    type_items_dict = dict()
    for item in arr:
        if type(item) == list:
            new_array.extend(recursive_array_sort(item))
        else:
            if type(item) == dict:
                sort_dict_array_items(item)
            _add_type_item(item)

    for dict_key in sorted(type_items_dict):
        if dict_key == 'dict' and len(type_items_dict[dict_key]) > 0 and len(type_items_dict[dict_key][0]) > 0:
            key = list(type_items_dict[dict_key][0].keys())[0]
            new_array.extend(sorted(type_items_dict[dict_key], key=lambda x: x[key]))
        else:
            new_array.extend(sorted(type_items_dict[dict_key]))
    return new_array


def sort_dict_array_items(dict_item):
    for k, v in dict_item.items():
        if type(v) == list:
            dict_item[k] = recursive_array_sort(v)


def is_partial_dict_match_in_arr(dict_var, arr):
    for arr_item in arr:
        if type(arr_item) == dict:
            if partial_dict_match(dict_var, arr_item):
                return True
    return False


def partial_dict_match(src, other):
    for key, val in src.items():
        if val is not None:
            if key in other and other[key] is not None and other[key] != val:
                if type(val) == list and type(other[key]) == list:
                    for arr_item in val:
                        if arr_item not in other[key]:
                            if isinstance(arr_item, RadwareParametersStruct):
                                if not arr_item.is_partial_struct_match_in_arr(other[key]):
                                    return False
                            if type(arr_item) == dict:
                                if not is_partial_dict_match_in_arr(arr_item, other[key]):
                                    return False
                            return False
                else:
                    return False
    return True


def generate_password(mac_address: str, file_size: int, http_proxy_url=None):
    rest = RestSession(http_proxy_url=http_proxy_url)
    if http_proxy_url:
        use_proxy = True
    else:
        use_proxy = False

    mac_address = mac_address.replace(':', '')
    r = rest.request('POST', RADWARE_PASSWORD_URL, json={'mac': mac_address, 'filesize': file_size},
                     use_http_proxy=use_proxy)
    if r.ok:
        r_json = r.json()
        if 'data' in r_json and 'password' in r_json['data']:
            log.debug('Device_MAC: {0} , image_size: {1} Upgrade_password: {2}'.format(mac_address, file_size,
                                                                                       r_json['data']['password']))
            return r_json['data']['password']

    raise RestRequestError(r)


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except IOError as e:
        raise FunctionError(get_file_size, e)


class RadwareParametersExtension(object):
    __metaclass__ = ABCMeta


class PasswordArgument(object):
    __metaclass__ = ABCMeta


class BaseEnum(Enum):
    __metaclass__ = ABCMeta

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


class Comparable(object):
    __metaclass__ = ABCMeta

    def compare(self, other) -> dict:
        diff = dict()
        if other is None:
            return diff
        if type(self) != type(other):
            raise ArgumentNotExpectedError(other, 'can not compare with type {0}'.format(type(self)))

        self_dict = self.obj_to_dict()
        other_dict = other.obj_to_dict()
        for k in self_dict.keys():
            if self_dict[k] != other_dict[k]:
                if type(self_dict[k]) == list and type(other_dict[k]) == list and len(self_dict[k]) == \
                        len(other_dict[k]):
                    if recursive_array_sort(self_dict[k]) != recursive_array_sort(other_dict[k]):
                        diff.update({k: other_dict[k]})
                else:
                    if type(other_dict[k]) == dict and type(self_dict[k]) == dict:
                        if sort_dict_array_items(other_dict[k]) == sort_dict_array_items(self_dict[k]):
                            diff.update({k: other_dict[k]})
                    else:
                        diff.update({k: other_dict[k]})
        return diff

    @abstractmethod
    def obj_to_dict(self):
        pass


class RadwareParametersStruct(Comparable):
    __metaclass__ = ABCMeta

    def __str__(self):
        return str(self.translate_to_dict())

    def __eq__(self, other):
        if not isinstance(other, RadwareParametersStruct):
            return False

        self_dict = self.translate_to_dict()
        other_dict = other.translate_to_dict()
        return self_dict == other_dict

    def obj_to_dict(self):
        return self.translate_to_dict()

    def get_required_fields(self) -> List[str]:
        required = list()
        annotations = get_type_hints(type(self))
        for k, v in annotations.items():
            if not is_annotation_type_optional(v):
                required.append(k)
        return required

    def copy_parameters_required_fields(self, from_parameters):
        if type(from_parameters) != type(self):
            raise ArgumentTypeError(type(self), from_parameters)
        for field in self.get_required_fields():
            if hasattr(from_parameters, field):
                setattr(self, field, getattr(from_parameters, field))

    def is_required_fields_match(self, other):
        self.validate(other)
        self.validate_required_fields(self)
        self.validate_required_fields(other)
        for field in self.get_required_fields():
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    def translate_to_dict(self):
        return self._param_translator(self)

    def _param_translator(self, struct) -> dict:
        new_dict = dict()
        for k, v in struct.__dict__.items():
            if isinstance(v, BaseEnum):
                new_dict[k] = v.name
            elif isinstance(v, list):
                new_arr = list()
                for item in v:
                    if isinstance(item, RadwareParametersStruct):
                        new_arr.append(self._param_translator(item))
                    else:
                        new_arr.append(item)
                new_dict[k] = new_arr
            elif isinstance(v, RadwareParametersStruct):
                new_dict[k] = self._param_translator(v)
            else:
                new_dict[k] = v
        return new_dict

    def _set_attributes(self, **params):
        self.__dict__.update(**params)

    def set_attributes(self, **params):
        self._set_attributes(**params)
        self.prepare_input_parameters(self)

    @classmethod
    def validate(cls, parameters):
        if type(parameters) != cls:
            raise ArgumentTypeError(cls, parameters)

    @classmethod
    def validate_prepare(cls, parameters, validate_required=True):
        cls.validate(parameters)
        if validate_required:
            cls.validate_required_fields(parameters)
        return cls.get_instance(**parameters.translate_to_dict())

    @classmethod
    def validate_required_fields(cls, parameters):
        required_fields = parameters.get_required_fields()
        for field in required_fields:
            if getattr(parameters, field) is None:
                raise ArgumentMissingError(cls, field)

    @classmethod
    def get_instance(cls, **params):
        instance = cls()
        instance._set_attributes(**params)
        return cls.prepare_input_parameters(instance)

    @staticmethod
    def prepare_input_parameters(parameters):
        annotations = get_type_hints(type(parameters))
        for k, v in parameters.__dict__.items():
            list_mode = False
            if v is not None:
                if k in annotations:
                    annotation_class = get_annotation_class(annotations[k])
                    if is_annotation_type_optional(annotations[k]):
                        if is_optional_type_list(annotations[k]):
                            list_mode = True
                    if is_annotation_type_list(annotations[k]):
                        list_mode = True

                    if list_mode:
                        tmp_list = list()
                        if issubclass(annotation_class, RadwareParametersStruct):
                            for list_item in v:
                                if type(list_item) != annotation_class:
                                    tmp_list.append(annotation_class.get_instance(**list_item))
                                else:
                                    tmp_list.append(list_item)
                            setattr(parameters, k, tmp_list)
                    else:
                        if issubclass(annotation_class, RadwareParametersStruct):
                            if type(v) != annotation_class:
                                if v and v is not None:
                                    setattr(parameters, k, annotation_class.get_instance(**v))
                        elif issubclass(annotation_class, BaseEnum):
                            if type(v) != annotation_class:
                                #support Enum override to limit allowed values
                                if type(v).__name__ == annotation_class.__name__ and v.name in \
                                        annotation_class.value_names():
                                    continue

                                if type(v) != int:
                                    setattr(parameters, k, annotation_class[v])
                                else:
                                    # support ENUMs missing in MIB  - which not being translate by the BaseBeanEnum
                                    setattr(parameters, k, annotation_class.enum(v))
                            else:
                                continue
        return parameters

    def is_partial_struct_match_in_arr(self, arr, arr_match_items=None):
        def _add_match_item(match_item):
            if arr_match_items is not None:
                if match_item not in arr_match_items:
                    arr_match_items.append(match_item)

        def _validate_compare_structs(other):
            self.validate_required_fields(other)
            if self.is_required_fields_match(other):
                other.overwrite_null_attrs(self)
                if other == self:
                    return True
            return False

        for item in arr:
            if type(item) == dict:
                tmp = type(self)()
                tmp.set_attributes(**item)
                result = _validate_compare_structs(tmp)
                if result:
                    _add_match_item(item)
                    return result
            elif isinstance(item, RadwareParametersStruct):
                result = _validate_compare_structs(item)
                if result:
                    _add_match_item(item)
                    return result

        return False

    def overwrite_null_attrs(self, other):
        for k, v in self.__dict__.items():
            if v is None:
                other_val = getattr(other, k)
                if other_val is not None:
                    setattr(self, k, other_val)

    def struct_normalization(self):
        # optional normalization procedure for non-deletable structs/ special treatment
        pass

    def clear_zero_ip_address(self):
        for k, v in self.__dict__.items():
            if v == '0.0.0.0' or v == '0:0:0:0:0:0:0:0':
                setattr(self, k, None)


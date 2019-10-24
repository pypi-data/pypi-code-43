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
from radware.sdk.exceptions import *
from abc import ABCMeta, abstractmethod
from radware.sdk.beans_common import BeanUtils, READ_PROP
from radware.sdk.common import RadwareParametersStruct,  PasswordArgument, \
    get_annotation_class, is_annotation_type_list_incl_optional_lookup, is_annotation_type_list, partial_dict_match
from radware.sdk.api import BaseAPI, ConfiguratorAPI, DeviceAPI
from typing import List, Union, get_type_hints

log = logging.getLogger(__name__)

MSG_UPDATE = ' updated successfully'
MSG_DELETE = ' deleted successfully'
MSG_DEPLOY = ' deployed successfully'
MSG_NO_DELETE = 'delete procedure not available on this class'
MSG_NO_DIFFERENTIAL_UPDATE = 'no differential update'
MSG_NO_CHANGE = 'no change'


class DryRunDeleteProcedure(object):
    def __init__(self,):
        self.ignore_all_props = False
        self.non_removable_bean_map_attrs_list = list()
        self.ignore_prop_by_value = dict()
        self.ignore_prop_names = list()


class ConfigManagerResult(object):
    def __init__(self, server=None, command=None, content=None, diff=None):
        self.server = server
        self.command = command
        self._content = content
        self.diff = diff

    @property
    def content_raw(self):
        return self._content

    @property
    def content_translate(self):
        if isinstance(self._content, RadwareParametersStruct):
            return self._content.translate_to_dict()
        elif isinstance(self._content, list):
            return self._translate_list_result()
        else:
            return self._content

    def _translate_list_result(self) -> List[dict]:
        new_result = list()
        for item in self._content:
            if item and isinstance(item, RadwareParametersStruct):
                new_result.append(item.translate_to_dict())
            else:
                new_result.append(item)
        return new_result

    def __str__(self):
        return 'Command: {2}, Server: {3} Result: {0}, Diff: {1}'.format(self.content_translate, self.diff,
                                                                         self.command, self.server)


class Configurator(BaseAPI):
    __metaclass__ = ABCMeta

    @staticmethod
    def _update_param_struct_attrs_from_object(struct, attrs_dict, obj):
        for k, v in attrs_dict.items():
            if hasattr(struct, v) and hasattr(obj, k):
                value = getattr(obj, k)
                setattr(struct, v, value)

    @staticmethod
    def _update_object_attrs_from_struct(struct, attrs_dict, obj):
        for k, v in attrs_dict.items():
            if hasattr(struct, v):
                value = getattr(struct, v)
                if value is not None:
                    setattr(obj, k, value)


class DeviceConfigurator(Configurator, ConfiguratorAPI):
    __metaclass__ = ABCMeta
    READ = 'read'
    UPDATE = 'update'
    DEPLOY = 'deploy'
    DELETE = 'delete'
    READ_ALL = 'read_all'

    def __init__(self, bean_map):
        Configurator.__init__(self)
        self._bean_map = bean_map
        self._beans = None
        log.info(' {0} initialized, server: {1}'.format(self.__class__.__name__, self.id))

    @property
    @abstractmethod
    def _device_api(self) -> DeviceAPI:
        pass

    @abstractmethod
    def _entry_bean_instance(self, parameters):
        pass

    def _validate_prepare_parameters(self, parameters, validate_required=True):
        return self.get_parameters_class().validate_prepare(parameters, validate_required)

    def _validate_parameters(self, parameters):
        self.get_parameters_class().validate(parameters)

    @abstractmethod
    def read(self, parameters: RadwareParametersStruct, validate_required=True, **kw) -> RadwareParametersStruct:
        pass

    @abstractmethod
    def update(self, parameters: RadwareParametersStruct, dry_run=False, remove_items: RadwareParametersStruct = None,
               **kw) -> str:
        pass

    def delete(self, parameters: RadwareParametersStruct, dry_run=False, **kw) -> str:
        log.debug(' {0}: {1}, server: {2}, params: {3}'.format(self.__class__.__name__, self.DELETE.upper(), self.id,
                                                               parameters))
        prepared_params = self._validate_prepare_parameters(parameters)
        self_obj = self._entry_bean_instance(prepared_params)
        self._device_api.delete(self_obj, dry_run=dry_run)
        return self._get_object_id(prepared_params) + MSG_DELETE

    def deploy(self, parameters: RadwareParametersStruct, dry_run=False, **kw) -> str:
        self.delete(parameters, dry_run, **kw)
        self.update(parameters, dry_run, **kw)
        return self._get_object_id(parameters) + MSG_DEPLOY

    def read_all(self, parameters: RadwareParametersStruct = None, **kw) -> List[RadwareParametersStruct]:
        def _read_add_result(validate_required=True):
            res = self.read(parameters, validate_required, **kw)
            if res is not None:
                result.append(res)

        log.debug(' {0}: {1}, server: {2}, params: {3}, args: {4}'.format(self.__class__.__name__, self.READ_ALL.upper(),
                                                                          self.id, parameters, kw))
        entry_bean = self._entry_bean_instance(parameters)
        result = list()
        if entry_bean.__class__ in self._bean_map:
            if hasattr(entry_bean, 'get_index_names'):
                attrs = self._bean_map[entry_bean.__class__]['attrs']
                params_class = self._bean_map[entry_bean.__class__]['struct']
                beans = self._device_api.read_all(entry_bean)
                if beans:
                    for bean in beans:
                        parameters = params_class()
                        self._update_param_struct_attrs_from_object(parameters, attrs, bean)
                        _read_add_result()
            else:
                if parameters is None:
                    parameters = self.get_parameters_class()()
                _read_add_result(False)
        else:
            if parameters is None:
                parameters = self.get_parameters_class()()
            _read_add_result()
        return result

    def _get_object_id(self, parameters):
        id_str = ''
        bean_instance = self._entry_bean_instance(parameters)
        if hasattr(bean_instance, 'get_index_names'):
            for idx in bean_instance.get_index_names():
                val = getattr(bean_instance, idx)
                if val:
                    id_str += '{0} ,'.format(val)

            return id_str[:len(id_str)-2]
        return id_str

    def _get_bean_instance(self, bean_class, parameters, bean_attr_map=None):
        if bean_class is None:
            return
        bean_instance = bean_class()
        if not bean_attr_map:
            attr_mapping = self._bean_map[bean_class]['attrs']
        else:
            attr_mapping = bean_attr_map
        if not parameters:
            return bean_instance
        if hasattr(bean_instance, 'get_index_names'):
            for idx in bean_instance.get_index_names():
                if idx in attr_mapping:
                    if hasattr(parameters, attr_mapping[idx]):
                        val = getattr(parameters, attr_mapping[idx])
                        if val is not None:
                            setattr(bean_instance, idx, val)
        else:
            if bean_attr_map:
                for k, v in bean_attr_map.items():
                    setattr(bean_instance, k, READ_PROP)
        return bean_instance

    def _struct_load(self, parameters):
        if self._beans:
            tmp_struct = type(parameters)()
            annotations = get_type_hints(type(parameters))
            for bean_class, bean_keys in self._bean_map.items():
                if bean_keys['direct']:
                    if bean_keys['struct'] == type(parameters):
                        self._update_param_struct_attrs_from_object(tmp_struct, bean_keys['attrs'],
                                                                    self._beans[bean_class])
                    else:
                        if not is_annotation_type_list(bean_keys['struct']):
                            for attr_key, attr_val in parameters.__dict__.items():
                                annotation_class = get_annotation_class(annotations[attr_key])
                                if bean_keys['struct'] == annotation_class:
                                    self._update_param_struct_attrs_from_object(getattr(tmp_struct, attr_key),
                                                                                bean_keys['attrs'],
                                                                                self._beans[bean_class])
                                    break
                        else:
                            for attr_key, attr_val in parameters.__dict__.items():
                                annotation_class = get_annotation_class(annotations[attr_key])
                                if is_annotation_type_list_incl_optional_lookup(annotations[attr_key]) and \
                                        get_annotation_class(bean_keys['struct']) == annotation_class:
                                    new_param_val = list()
                                    for bean in self._beans[bean_class]:
                                        new_struct = annotation_class()
                                        self._update_param_struct_attrs_from_object(new_struct, bean_keys['attrs'],
                                                                                    bean)
                                        new_param_val.append(new_struct)
                                    setattr(tmp_struct, attr_key, new_param_val)
                                    break
            for k, v in tmp_struct.__dict__.items():
                setattr(parameters, k, v)

    def _read_device_beans(self, parameters):
        self._beans = dict()
        exist = False
        for bean_class, bean_keys in self._bean_map.items():
            bean_instance = self._get_bean_instance(bean_class, parameters, bean_keys['attrs'])
            if not is_annotation_type_list(bean_keys['struct']):
                self._beans[bean_class] = self._device_api.read(bean_instance)
            else:
                self._beans[bean_class] = self._device_api.read_all(bean_instance)

            if self._beans[bean_class]:
                exist = True
        if not exist:
            self._beans = None
        else:
            self._struct_load(parameters)

    def _write_device_beans(self, parameters, dry_run=False, direct_exclude=None):
        for bean_class, bean_keys in self._bean_map.items():
            if bean_keys['direct']:
                if direct_exclude is not None and bean_class in direct_exclude:
                    continue
                if bean_keys['struct'] == type(parameters):
                    self._write_bean_attrs(parameters, bean_keys['attrs'], bean_class, dry_run=dry_run)
                else:
                    if not is_annotation_type_list(bean_keys['struct']):
                        for attr_key, attr_val in parameters.__dict__.items():
                            if bean_keys['struct'] == type(attr_val):
                                self._write_bean_attrs(attr_val, bean_keys['attrs'], bean_class, dry_run=dry_run)
                                break
                    else:
                        for attr_key, attr_val in parameters.__dict__.items():
                            item_class = get_annotation_class(bean_keys['struct'])
                            if type(attr_val) == list and attr_val:
                                for item in attr_val:
                                    if type(item) == item_class:
                                        self._write_bean_attrs(item, bean_keys['attrs'], bean_class, dry_run=dry_run)
                                    else:
                                        raise ArgumentTypeError(item_class, item)
                                break

    def _write_bean_attrs(self, params, attr_map, bean_class, pre_index_dict=None, dry_run=False):
        #bean_instance = self._get_bean_instance(bean_class, params, attr_map)
        bean_instance = self._get_bean_instance(bean_class, params)
        if hasattr(bean_instance, 'get_index_names'):
            index_names = bean_instance.get_index_names()
        else:
            index_names = tuple()
        if pre_index_dict is not None:
            if pre_index_dict is not None:
                for k, v in pre_index_dict.items():
                    setattr(bean_instance, k, v)
        self._update_object_attrs_from_struct(params, attr_map, bean_instance)
        for k, v in bean_instance.__dict__.items():
            # verify object not empty
            if k not in index_names and v is not None:
                self._device_api.update(bean_instance, dry_run=dry_run)
                break

    def _get_bean_used_numeric_indexes(self, bean, lookup_index_name):
        used_indexes = list()
        current_beans = self._device_api.read_all(bean)
        for item in current_beans:
            used_indexes.append(getattr(item, lookup_index_name))
        return used_indexes

    def _get_bean_free_index(self, bean, idx_property_name):
        result = self._device_api.read(bean)
        if result:
            return getattr(result, idx_property_name)

    def _assign_write_numeric_index_beans(self, bean_class, param_collection, pre_index_dict=None, dry_run=False):
        instance = bean_class()
        index_name = None
        if hasattr(instance, 'get_index_names'):
            index_names = instance.get_index_names()
            if len(index_names) > 1:
                if pre_index_dict is None:
                    raise DeviceConfiguratorError(self.__class__, 'assign update numeric index beans error,  bean '
                                                                  'class: {0} has multiple indexes'.format(bean_class))
                else:
                    for idx_name in index_names:
                        if idx_name not in pre_index_dict:
                            index_name = idx_name
                            break
            else:
                index_name = index_names[0]
        else:
            raise DeviceConfiguratorError(self.__class__, 'assign update numeric index beans error,  bean class: {0} '
                                                          'has no indexes'.format(bean_class))
        if index_name is None:
            raise DeviceConfiguratorError(self.__class__, 'assign update numeric index beans error,  bean class: {0} '
                                                          'index name not found'.format(bean_class))
        used_indexes = self._get_bean_used_numeric_indexes(bean_class(), index_name)
        if param_collection is not None:
            for item in param_collection:
                if pre_index_dict is None:
                    pre_index_dict = dict()
                pre_index_dict.update({index_name: BeanUtils.get_next_available_numeric_idx(used_indexes)})
                self._write_bean_attrs(item, self._bean_map[bean_class]['attrs'], bean_class, pre_index_dict, dry_run)

    def _write_bean_collection(self, bean_class, param_collection, pre_index_dict=None, dry_run=False):
        for item in param_collection:
            self._write_bean(bean_class, item, pre_index_dict, dry_run=dry_run)

    def _write_bean(self, bean_class, param, pre_index_dict=None, dry_run=False):
        self._write_bean_attrs(param, self._bean_map[bean_class]['attrs'], bean_class, pre_index_dict, dry_run=dry_run)

    def _remove_device_beans_by_struct_collection(self, param_collection, dry_run=False):
        if param_collection and len(param_collection) > 0:
            struct_type = type(param_collection[0])
            bean_class = None
            for k, v in self._bean_map.items():
                if v['struct'] == List[struct_type]:
                    bean_class = k
                    break
            if not bean_class:
                raise DeviceConfiguratorError(self.__class__, 'no bean class in bean_map for struct type: {0}'.
                                              format(struct_type))

            beans = self._device_api.read_all(bean_class())
            if beans:
                for item in param_collection:
                    if type(item) != struct_type:
                        raise DeviceConfiguratorError(self.__class__, 'struct collection items should be of the '
                                                                      'same type for bean removal')
                    attrs = self._bean_map[bean_class]['attrs']
                    for bean in beans:
                        tmp_struct = struct_type()
                        self._update_param_struct_attrs_from_object(tmp_struct, attrs, bean)
                        tmp_struct.struct_normalization()
                        if tmp_struct == item:
                            self._device_api.delete(bean, dry_run=dry_run)
                            break

    def _remove_device_beans_by_simple_collection(self, simple_collection, lookup_bean, prop_name, dry_run=False):
        if simple_collection:
            beans = self._device_api.read_all(lookup_bean)
            if beans:
                for bean in beans:
                    val = getattr(bean, prop_name)
                    if val in simple_collection:
                        self._device_api.delete(bean, dry_run=dry_run)


class NumericConfigurator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def _entry_bean_instance(self, parameters):
        pass

    @abstractmethod
    def _validate_parameters(self, parameters):
        pass

    @property
    @abstractmethod
    def _device_api(self) -> DeviceAPI:
        pass

    @property
    @abstractmethod
    def id(self):
        pass

    def free_index(self, parameters: RadwareParametersStruct = None, start_idx=1, **kw) -> int:
        def _handle_int_idx(val):
            if val is None:
                return 1
            if val < 1:
                return 1
            else:
                return val

        if parameters is not None:
            self._validate_parameters(parameters)
            required_fields = parameters.get_required_fields()
            idx = getattr(parameters, required_fields[0])
            if idx is not None:
                start_idx = _handle_int_idx(idx)
            else:
                start_idx = _handle_int_idx(start_idx)
        else:
            start_idx = _handle_int_idx(start_idx)

        entry_bean_instance = self._entry_bean_instance(None)
        numeric_index_items = self._device_api.read_all(entry_bean_instance)
        if not numeric_index_items:
            result = start_idx
        else:
            index_name = numeric_index_items[0].get_index_names()[0]
            for bean in numeric_index_items:
                cur_idx = getattr(bean, index_name)
                if type(cur_idx) != int:
                    cur_idx = int(cur_idx)
                if cur_idx < start_idx:
                    continue
                elif cur_idx != start_idx:
                    return start_idx
                start_idx += 1
            result = start_idx

        log.debug(' {0}: free_index, server: {1}, params: {2}, next_index: {3}'.format(self.__class__.__name__, self.id,
                                                                                       parameters, result))
        return result


class DeviceConfigurationManager(object):
    __metaclass__ = ABCMeta

    DIFF_APPEND_KEY = '+++'
    DIFF_REMOVE_KEY = '---'
    DIFF_ADD_CFG_KEY = 'added'
    DIFF_REMOVE_CFG_KEY = 'removed'
    DIFF_DUPLICATES = 'duplicates'

    def execute(self, configurator: DeviceConfigurator, command, parameters: Union[RadwareParametersStruct, None],
                **kw):
        if self._is_write_function(configurator, command):
            res, diff = self._execute_write_function(configurator, command, parameters, **kw)
            result = ConfigManagerResult(configurator.id, command, res, diff)
        else:
            result = ConfigManagerResult(configurator.id, command, self._execute_function(configurator, command,
                                                                                          parameters, **kw))
        log.debug(result)
        return result

    def _execute_function(self, configurator, func_name, parameters, **kw):
        func = self._get_function(configurator, func_name)
        try:
            return func(parameters, **kw)
        except TypeError as e:
            raise FunctionError(func, e)

    def _execute_write_function(self, configurator, func_name, parameters, dry_run=False, differential=False,
                                write_on_change=False, get_diff=False, **kw):

        def _remove_array_entries(map_var):
            for k, v in list(map_var.items()):
                if type(v) == list:
                    map_var.pop(k)
                elif type(v) == dict():
                    _remove_array_entries(v)

        def _get_diff():
            if get_diff:
                if dry_run:
                    if self._get_config_function(configurator, func_name) == configurator.update:
                        if differential:
                            return dry_run_diff
                        diff_append_result = self._get_dry_run_diff_append(dry_run_diff)
                        diff_duplicate_result = self._get_dry_run_diff_duplicates(dry_run_diff)
                        if diff_append_result or diff_duplicate_result:
                            update_diff_result = {}
                            if diff_append_result:
                                update_diff_result.update({self.DIFF_APPEND_KEY: diff_append_result})
                            if diff_duplicate_result:
                                update_diff_result.update({self.DIFF_DUPLICATES: diff_duplicate_result})
                            diff_remove_result = self._get_dry_run_diff_remove(dry_run_diff)
                            if diff_remove_result:
                                _remove_array_entries(diff_remove_result)
                                if diff_remove_result:
                                    update_diff_result.update({self.DIFF_REMOVE_KEY: diff_remove_result})
                            return update_diff_result
                    else:
                        return dry_run_diff
                else:
                    after_config = configurator.read(parameters)
                    return self._get_device_changes(after_config, before_config)

        def _prepare_update_params(attrs):
            params = type(parameters)()
            try:
                params.copy_parameters_required_fields(parameters)
                if attrs:
                    params.set_attributes(**attrs)
                return params
            except TypeError:
                raise ArgumentTypeError(RadwareParametersStruct, params)

        if not self._is_write_function(configurator, func_name):
            raise FunctionError(func_name, 'function not a write function')

        log.debug(' {0}: write function, device: {1}, dry_run: {2}, differential: {3}, write_on_change: {4}, '
                  'get_diff: {5}, params: {6}, args: {7}'.format(self.__class__.__name__, configurator.id, dry_run,
                                                                 differential, write_on_change, get_diff, parameters,
                                                                 kw))
        if get_diff:
            before_config = configurator.read(parameters)
        else:
            before_config = None
        diff = None
        dry_run_diff = None
        if differential:
            if self._get_config_function(configurator, func_name) == configurator.update:
                dry_run_diff = self._dry_run_evaluation(configurator, func_name, parameters, differential)
                diff_append = self._get_dry_run_diff_append(dry_run_diff)
                diff_remove = self._get_dry_run_diff_remove(dry_run_diff)

                if diff_remove:
                    rem_items = _prepare_update_params(diff_remove)
                else:
                    rem_items = None

                if diff_append or diff_remove:
                    new_parameters = _prepare_update_params(diff_append)
                    result = self._execute_function(configurator, func_name, new_parameters, dry_run=dry_run,
                                                    remove_items=rem_items, **kw)
                    diff = _get_diff()
                    return result, diff
                else:
                    return MSG_NO_DIFFERENTIAL_UPDATE, diff
        if write_on_change:
            dry_run_diff = self._dry_run_evaluation(configurator, func_name, parameters, differential)

            if self._get_config_function(configurator, func_name) == configurator.update:
                if self._pending_append_change(dry_run_diff):
                    result = self._execute_function(configurator, func_name, parameters, dry_run=dry_run, **kw)
                else:
                    if self.DIFF_DUPLICATES in dry_run_diff:
                        dry_run_diff.pop(self.DIFF_DUPLICATES)
                    result = MSG_NO_CHANGE
            else:
                if self._pending_change(dry_run_diff):
                    result = self._execute_function(configurator, func_name, parameters, dry_run=dry_run, **kw)
                else:
                    if self.DIFF_DUPLICATES in dry_run_diff:
                        dry_run_diff.pop(self.DIFF_DUPLICATES)
                    result = MSG_NO_CHANGE
        else:
            if dry_run:
                dry_run_diff = self._dry_run_evaluation(configurator, func_name, parameters, differential)
            result = self._execute_function(configurator, func_name, parameters, dry_run=dry_run, **kw)
        diff = _get_diff()
        return result, diff

    def _is_write_function(self, configurator: DeviceConfigurator, func_name: str) -> bool:
        func = self._get_config_function(configurator, func_name)
        return func == configurator.delete or func == configurator.deploy or func == configurator.update

    def _get_device_changes(self, after_config, before_config):
        if not before_config == after_config:
            changes = dict()
            changes.update({self.DIFF_ADD_CFG_KEY: self.get_diff(after_config, before_config)})
            changes.update({self.DIFF_REMOVE_CFG_KEY: self.get_diff(before_config, after_config)})
            return changes

    def _get_function(self, configurator, func_name):
        func = self._get_config_function(configurator, func_name)
        if not callable(func):
            raise FunctionError(func, 'not callable')
        return func

    @staticmethod
    def _strip_diff_array_items(diff_result, config):
        if config is None:
            return
        current_config_dict = config.translate_to_dict()
        for k, v in list(diff_result.items()):
            if k in current_config_dict:
                if type(v) == list and type(current_config_dict[k]) == list:
                    result_array = list()
                    for item in v:
                        if item not in current_config_dict[k]:
                            result_array.append(item)
                    if not result_array:
                        diff_result.pop(k)
                    else:
                        diff_result[k] = result_array

    def get_diff(self, config, from_config):
        result = dict()
        if from_config is not None:
            diff = from_config.compare(config)
            for k, v in diff.items():
                if v is not None:
                    result.update({k: v})
        else:
            if config is None:
                return result
            for k, v in config.translate_to_dict().items():
                if v is not None:
                    result.update({k: v})
        self._strip_diff_array_items(result, from_config)
        return result

    def _dry_run_delete_diff_normalization(self, configurator, diff, append_diff=None):
        result = configurator.dry_run_delete_procedure(diff)
        if result:
            if type(result) != DryRunDeleteProcedure:
                raise ArgumentTypeError(DryRunDeleteProcedure, result)
            if result.ignore_all_props:
                self._remove_all_non_delete(diff)
            else:
                if result.ignore_prop_names:
                    for prop in result.ignore_prop_names:
                        if prop in diff:
                            diff.pop(prop)
                if result.ignore_prop_by_value:
                    self._remove_by_value(diff, result.ignore_prop_by_value, append_diff)
                if result.non_removable_bean_map_attrs_list:
                    for item in result.non_removable_bean_map_attrs_list:
                        self.remove_non_removable_by_bean_map_attrs(diff, item, result.ignore_prop_by_value, append_diff)

    def _dry_run_evaluation(self, configurator, func_name, parameters, differential):

        def _dry_run_update(remove_mode):
            updated_attrs = self._dry_run_result_normalization(parameters, before_config, remove_mode)
            after_config.set_attributes(**updated_attrs)
            diff = self.get_diff(after_config, before_config)
            return diff

        def _dry_run_remove():
            if before_config is not None:
                diff = self.get_diff(before_config, after_config)
                self._dry_run_delete_diff_normalization(configurator, diff, append_diff)
                return diff
            else:
                return dict()

        def _dry_run_delete():
            diff = before_config.translate_to_dict()
            for k, v in list(diff.items()):
                if type(v) == list and not v:
                    diff.pop(k)
            self._dry_run_delete_diff_normalization(configurator, diff)
            return diff

        before_config = configurator.read(parameters)
        changes = dict()
        func = self._get_config_function(configurator, func_name)
        if func == configurator.update:
            after_config = type(parameters)()
            if differential:
                append_diff = _dry_run_update(True)
            else:
                append_diff = _dry_run_update(False)
            remove_diff = _dry_run_remove()
            if append_diff:
                changes.update({self.DIFF_APPEND_KEY: append_diff})
            if remove_diff:
                changes.update({self.DIFF_REMOVE_KEY: remove_diff})
            if not differential:
                duplicates = self._dry_run_duplicates(before_config, parameters)
                if duplicates:
                    changes.update({self.DIFF_DUPLICATES: duplicates})

        elif func == configurator.deploy:
            after_config = type(parameters)()
            append_diff = _dry_run_update(True)
            remove_diff = _dry_run_remove()
            if append_diff or remove_diff:
                changes.update({self.DIFF_APPEND_KEY: append_diff})
                changes.update({self.DIFF_REMOVE_KEY: remove_diff})
        elif func == configurator.delete:
            if before_config is not None:
                delete_diff = _dry_run_delete()
                if delete_diff:
                    changes.update({self.DIFF_REMOVE_KEY: delete_diff})
        else:
            raise DeviceConfiguratorError(configurator, 'no dry run procedure for function: {0}'.
                                          format(func_name))
        return changes

    def _dry_run_result_normalization(self, parameters, current_config, remove_mode=False):
        if not type(parameters) == dict:
            attrs_dict = parameters.translate_to_dict()
        else:
            attrs_dict = parameters
        dict_result = dict()
        for k, v in attrs_dict.items():
            cur_cfg_attr_val = None
            if current_config is not None and hasattr(current_config, k):
                cur_cfg_attr_val = getattr(current_config, k)
            if type(v) == dict:
                dict_result.update({k: self._dry_run_result_normalization(v, cur_cfg_attr_val, remove_mode)})
            elif type(v) == list:
                if type(cur_cfg_attr_val) == list:
                    dict_result.update({k: self._dry_run_array_normalization(v, cur_cfg_attr_val, remove_mode)})
                else:
                    dict_result.update({k: v})

            elif v is not None:
                if current_config is not None:
                    annotations = get_type_hints(type(current_config))
                    annotation_class = get_annotation_class(annotations[k])
                    if annotation_class != PasswordArgument:
                        dict_result.update({k: v})
                    else:
                        if cur_cfg_attr_val is not None:
                            dict_result.update({k: cur_cfg_attr_val})
                else:
                    dict_result.update({k: v})
            else:
                if cur_cfg_attr_val is not None:
                    if not remove_mode:
                        dict_result.update({k: cur_cfg_attr_val})
                    else:
                        if not isinstance(cur_cfg_attr_val, RadwareParametersStruct):
                            if type(cur_cfg_attr_val) == dict or type(cur_cfg_attr_val) == list:
                                if cur_cfg_attr_val:
                                    raise ArgumentNotExpectedTypeError(cur_cfg_attr_val, 'should be basic type instance')
                            dict_result.update({k: cur_cfg_attr_val})
                        else:
                            has_data = False
                            cur_cfg_attr_val.struct_normalization()
                            for k2, v2 in cur_cfg_attr_val.translate_to_dict().items():
                                if v2:
                                    has_data = True
                                    break
                            if has_data:
                                dict_result.update({k: None})
                            else:
                                dict_result.update({k: cur_cfg_attr_val})
                else:
                    dict_result.update({k: None})
        return dict_result

    @staticmethod
    def _get_config_function(configurator, func_name):
        try:
            return getattr(configurator, func_name)
        except AttributeError:
            raise DeviceConfiguratorError(configurator, 'function {0} not found'.format(func_name))

    @staticmethod
    def _dry_run_array_normalization(arr: list, cur_arr: list, remove_mode=False):
        new_arr = list()
        arr_match_items = list()

        for item in cur_arr:
            if isinstance(item, RadwareParametersStruct):
                item.struct_normalization()
                if item.is_partial_struct_match_in_arr(arr, arr_match_items):
                    new_arr.append(item)
            elif type(item) == list or type(item) == dict:
                raise ArgumentNotExpectedTypeError(item, 'should be RadwareParametersStruct or basic type instance')
            else:
                if remove_mode:
                    if item in arr and item not in new_arr:
                        new_arr.append(item)
                else:
                    if item not in new_arr:
                        new_arr.append(item)

        for item in arr:
            if item not in arr_match_items:
                if item not in new_arr:
                    new_arr.append(item)
        return new_arr

    @staticmethod
    def remove_non_removable_by_bean_map_attrs(diff_dict, non_removable_bean_attrs, exclude_map, append_diff=None):
        if not exclude_map:
            exclude_map = dict()
        for k, v in non_removable_bean_attrs.items():
            if v in diff_dict and v not in exclude_map:
                if not append_diff:
                    diff_dict.pop(v)
                else:
                    if v in append_diff and append_diff[v] == diff_dict[v]:
                        diff_dict.pop(v)

    @staticmethod
    def _remove_by_value(diff_dict, value_dict, append_diff=None):
        for k, v in value_dict.items():
            if k in diff_dict and diff_dict[k] == v:
                if not append_diff:
                    diff_dict.pop(k)
                else:
                    if k in append_diff and append_diff[k] == diff_dict[k]:
                        diff_dict.pop(k)

    @staticmethod
    def _remove_all_non_delete(diff_dict):
        for k in list(diff_dict.keys()):
            diff_dict.pop(k)

    def _get_dry_run_diff_append(self, dry_run_diff):
        if dry_run_diff is not None and self.DIFF_APPEND_KEY in dry_run_diff:
            return dry_run_diff[self.DIFF_APPEND_KEY]

    def _get_dry_run_diff_remove(self, dry_run_diff):
        if dry_run_diff is not None and self.DIFF_REMOVE_KEY in dry_run_diff:
            return dry_run_diff[self.DIFF_REMOVE_KEY]

    def _get_dry_run_diff_duplicates(self, dry_run_diff):
        if dry_run_diff is not None and self.DIFF_DUPLICATES in dry_run_diff:
            return dry_run_diff[self.DIFF_DUPLICATES]

    @staticmethod
    def _dry_run_duplicates(before_config, parameters):
        if before_config is not None:
            duplicates = dict()
            params_dict = parameters.translate_to_dict()
            for k, v in before_config.translate_to_dict().items():
                if type(v) == list:
                    duplicate_list = list()
                    if k in params_dict and type(params_dict[k]) == list:
                        for item in v:
                            if item in params_dict[k]:
                                if v not in duplicate_list:
                                    duplicate_list.append(item)
                            else:
                                if type(item) == dict:
                                    for arr_item in params_dict[k]:
                                        if type(arr_item) == dict and partial_dict_match(item, arr_item):
                                            if item not in duplicate_list:
                                                duplicate_list.append(item)
                                            break
                        if duplicate_list:
                            duplicates.update({k: duplicate_list})
            if duplicates:
                return duplicates

    def _pending_change(self, dry_run_diff):
        if self.DIFF_REMOVE_KEY in dry_run_diff:
            if dry_run_diff[self.DIFF_REMOVE_KEY]:
                return True
        if self.DIFF_APPEND_KEY in dry_run_diff:
            if dry_run_diff[self.DIFF_APPEND_KEY]:
                return True
        return False

    def _pending_append_change(self, dry_run_diff):
        if self.DIFF_APPEND_KEY in dry_run_diff:
            if dry_run_diff[self.DIFF_APPEND_KEY]:
                return True
        return False

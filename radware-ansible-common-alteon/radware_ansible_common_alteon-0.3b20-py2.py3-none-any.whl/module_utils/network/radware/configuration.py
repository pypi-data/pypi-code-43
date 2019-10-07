#!/usr/bin/python
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from abc import abstractmethod
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.radware.common import BaseAPI, RadwareModuleError, radware_server_argument_spec, \
    build_specs_from_annotation
try:
    from radware.sdk.api import BaseDeviceConnection
    from radware.sdk.exceptions import RadwareError
    from radware.sdk.management import DeviceManagement
    from radware.sdk.configurator import DeviceConfigurationManager, ConfigManagerResult
except ModuleNotFoundError:
    AnsibleModule(argument_spec={}, check_invalid_arguments=False).fail_json(
        msg="The radware-sdk-common package is required")


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
module: Device Configurator module
author:
  - Leon Meguira (@leonmeguira)
'''


class ConfigurationArgumentSpec(object):
    def __init__(self, config_class):
        self.supports_check_mode = True
        argument_spec = dict(
            parameters=dict(
                required=False,
                type='dict',
                options=build_specs_from_annotation(config_class.get_parameters_class())
            ),
            command=dict(
                required=True,
                choices=config_class.api_function_names()
            ),
            write_on_change=dict(
                required=False,
                type='bool',
                default=False
            ),
            differential_update=dict(
                required=False,
                type='bool',
                default=False
            )
        )
        self.argument_spec = {}
        self.argument_spec.update(radware_server_argument_spec)
        self.argument_spec.update(argument_spec)


class ConfigurationModule(BaseAPI):
    def __init__(self, configurator_class, **kwargs):
        self._configurator = configurator_class(self._device_connection)
        self._config_manager = DeviceConfigurationManager()
        self._command = self._base.params['command']
        self._write_on_change = self._base.params['write_on_change']
        self._differential_update = self._base.params['differential_update']
        self.arguments = configurator_class.get_parameters_class()()
        if self._base.params['parameters'] is None:
            self._base.params['parameters'] = dict()
        self.arguments.set_attributes(**self._base.params['parameters'])
        self.result = {}
        self.changed = False
        self.changes = None
        if hasattr(self._base.module, '_diff'):
            self._report_diff = getattr(self._base.module, '_diff')
        else:
            self._report_diff = False

    @abstractmethod
    def _on_error(self):
        pass

    @property
    def command(self):
        return self._command

    def exec_module(self):
        try:
            self._device_mng.verify_device_accessible(retries=2)
        except RadwareError as e:
            raise RadwareModuleError(e)

        try:
            conf_mng_result = self._config_manager.execute(self._configurator, self.command, self.arguments,
                                                           dry_run=self._base.module.check_mode,
                                                           differential=self._differential_update,
                                                           write_on_change=self._write_on_change,
                                                           get_diff=True)
            if conf_mng_result.diff:
                self.changed = True
                self.changes = conf_mng_result.diff
        except RadwareError as e:
            self._on_error()
            raise RadwareModuleError(e)

        if self.changed:
            self.result.update(dict(changed=self.changed))
            if self._report_diff:
                self.result.update(dict(diff=self.changes))
        self.result.update(command=self.command, result=conf_mng_result.content_translate)
        return self.result



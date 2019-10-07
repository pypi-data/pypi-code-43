#!/usr/bin/python
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import traceback

from ansible.module_utils.network.radware.common import RadwareModuleError
from ansible.module_utils.network.radware.alteon import AlteonManagementArgumentSpec, AlteonManagementModule
from radware.alteon.sdk.alteon_managment import AlteonMngConfig


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
module: alteon_mng_config
short_description: Manage configuration in Radware Alteon
description:
  - Manage configuration in Radware Alteon.
  - commit and commit_save not raise exception, instead they report state and fail_reason. in such of failure config 
  revert is called
version_added: null
author: 
  - Leon Meguira (@leonmeguira)
  - Nati Fridman (@natifridman)
options:
  provider:
    description:
      - Radware Alteon connection details.
    required: true
    suboptions:
      server:
        description:
          - Radware Alteon IP.
        required: true
        default: null
      user:
        description:
          - Radware Alteon username.
        required: true
        default: null
      password:
        description:
          - Radware Alteon password.
        required: true
        default: null
      validate_certs:
        description:
          - If C(no), SSL certificates will not be validated.
          - This should only set to C(no) used on personally controlled sites using self-signed certificates.
        required: true
        default: null
        type: bool
      https_port:
        description:
          - Radware Alteon https port.
        required: true
        default: null
      ssh_port:
        description:
          - Radware Alteon ssh port.
        required: true
        default: null
      timeout:
        description:
          - Timeout for connection.
        required: true
        default: null
  command:
    description:
      - Action to run.
    required: true
    default: null
    choices:
    - apply
    - commit
    - commit_save
    - diff
    - diff_flash
    - pending_configuration_validation
    - revert
    - revert_apply
    - save
    - sync
notes:
  - Requires Radware alteon Python SDK.
requirements:
  - Radware alteon Python SDK.
'''

EXAMPLES = r'''
- name: alteon configuration command
  alteon_mng_config:
    provider: 
      server: 192.168.1.1
      user: admin
      password: admin
      validate_certs: no
      https_port: 443
      ssh_port: 22
      timeout: 5
    command: apply
'''

RETURN = r'''
result:
  description: Message detailing run result
  returned: success
  type: str
  sample: complete
  sample2: {"state": "\nAlteon Function Error:\nFunction: <bound method AlteonMngConfig.apply of 
      <radware.alteon.sdk.alteon_managment.AlteonMngConfig object at 0x7f4c249e4c50>>\nStatus: 
      EnumAgApplyConfig.failed\nReason: [{'Index': 1, 'StringVal': \"Error: Enabled virtual server virt1 has no IP address.
      U+0085Error: Apply not done.  Use 'diff' to see pending changes,U+0085       
      then use configuration menus to correct errors.U+0085\"}]",
      "success": false}
'''


class ModuleManager(AlteonManagementModule):
    def __init__(self, **kwargs):
        super(ModuleManager, self).__init__(AlteonMngConfig, **kwargs)


def main():
    spec = AlteonManagementArgumentSpec(AlteonMngConfig)
    module = AnsibleModule(argument_spec=spec.argument_spec, supports_check_mode=spec.supports_check_mode)

    try:
        mm = ModuleManager(module=module)
        result = mm.exec_module()
        module.exit_json(**result)
    except RadwareModuleError as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

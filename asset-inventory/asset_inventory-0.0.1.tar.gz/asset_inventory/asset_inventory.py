from ansible import context
from ansible import constants
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager
from ansible.plugins.callback import CallbackBase
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict

from asset_inventory.models.server import Server
from asset_inventory.models.device import Device
from asset_inventory.models.inventory import Inventory

import json
import shutil
import collections


class ResultCallback(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)

        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result


class AssetManager():

    def __init__(self, remote_user, password):
        self.remote_user = remote_user
        self.password = password
        self.results_callback = ResultCallback()

    def fetch(self, hosts):
        if type(hosts) != list:
            hosts = [hosts]

        sources = ','.join(hosts)

        if len(hosts) == 1:
            sources += ','

        # since the API is constructed for CLI it expects certain options to always be set in the context object
        # spesify args that cannot be in play source
        context.CLIARGS = ImmutableDict(forks=10, timeout=3)

        # Takes care of finding and reading yaml, json and ini files
        loader = DataLoader()

        # create inventory, use path to host config file as source or hosts in a comma separated string
        inventory = InventoryManager(loader=loader, sources=sources)

        # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        passwords = dict(vault_pass='secret')

        for host in hosts:
            hostname = inventory.get_host(hostname=host)
            variable_manager.set_host_variable(host=hostname, varname='ansible_ssh_pass', value=self.password)

        # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally
        play_source = dict(hosts='all',
                           gather_facts='no',
                           connection='paramiko',
                           remote_user=self.remote_user,
                           tasks=[dict(action=dict(module='setup', args=''))])

        play = Play().load(data=play_source, variable_manager=variable_manager, loader=loader)

        tqm = None

        try:
            tqm = TaskQueueManager(inventory=inventory,
                                   variable_manager=variable_manager,
                                   loader=loader,
                                   passwords=passwords,
                                   stdout_callback=self.results_callback)

            run_result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

            # remove ansible tmpdir
            shutil.rmtree(constants.DEFAULT_LOCAL_TMP, True)

    def _desk_facts(self, results):
        devices = []
        for name, data in results['ansible_devices'].items():
            size = data['size']
            label = data['links']['labels']
            uuid = data['links']['uuids']

            device_dict = {
                'name': name,
                'size': size,
                'label': label,
                'uuid': uuid
            }

            device = Device(**device_dict)
            devices.append(device)
        return devices

    def _server_facts(self, results):

        distribution = results['ansible_distribution']
        distribution_version = results['ansible_distribution_version']
        memory = results['ansible_memtotal_mb']
        hostname = results['ansible_hostname']
        vendor = results['ansible_system_vendor']
        uptime = results['ansible_uptime_seconds']
        kernel = results['ansible_kernel']
        cpu = results['ansible_processor_vcpus']
        json = results['ansible_system']
        space = sum(mount['size_total'] for mount in results['ansible_mounts'])

        server_dict = {
            'distribution': distribution,
            'distribution_version': distribution_version,
            'memory': memory,
            'hostname': hostname,
            'vendor': vendor,
            'uptime': uptime,
            'kernel': kernel,
            'cpu': cpu,
            'space': space,
        }

        server = Server(**server_dict)
        return server

    def results(self):
        results = []
        Result = collections.namedtuple('Result', ['status', 'host', 'data'])

        for host, result in self.results_callback.host_ok.items():
            print(json.dumps(result._result['ansible_facts'], indent=2))
            server_facts = self._server_facts(result._result['ansible_facts'])
            devices_facts = self._desk_facts(result._result['ansible_facts'])
            inventory = Inventory(ip=host, server=server_facts, devices=devices_facts)
            result = Result(status='success', host=host, data=inventory.serialize())
            results.append(result)

        for host, result in self.results_callback.host_failed.items():
            result = Result(status='faild', host=host, data=result._result['msg'])
            results.append(result)

        for host, result in self.results_callback.host_unreachable.items():
            result = Result(status='unreachable', host=host, data=result._result['msg'])
            results.append(result)

        return results

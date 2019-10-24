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


class AssetManager:

    def __init__(self, remote_user, password, ssh_key, connection):
        self.remote_user = remote_user
        self.password = password
        self.ssh_key = ssh_key
        self.connection = connection

        self.results_callback = ResultCallback()

    def fetch(self, hosts):
        if type(hosts) != list:
            hosts = [hosts]

        sources = ','.join(hosts)

        if len(hosts) == 1:
            sources += ','

        # specify CLI args that cannot be in play source
        context.CLIARGS = ImmutableDict(forks=10, timeout=3, remote_user=self.remote_user, connection=self.connection)

        # takes care of finding and reading yaml, json and ini files
        loader = DataLoader()

        # create inventory, use path to host config file as source or hosts in a comma separated string
        inventory = InventoryManager(loader=loader, sources=sources)

        # merge all the different sources to give you a unified view of variables available in each context
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        for host in hosts:
            hostname = inventory.get_host(hostname=host)
            variable_manager.set_host_variable(host=hostname, varname='ansible_ssh_pass', value=self.password)
            # variable_manager.set_host_variable(host=hostname, varname='ansible_ssh_private_key_file', value=self.ssh_key)

        # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally
        play_source = dict(hosts='all',
                           gather_facts='no',
                           tasks=[dict(action=dict(module='setup', args=''))])

        play = Play().load(data=play_source, variable_manager=variable_manager, loader=loader)

        tqm = None
        passwords = dict(vault_pass='secret')

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
            vendor = data['vendor']
            ids = data['links']['ids']
            model = data['model']
            host = data['host']
            partitions = []

            for part_name, part_data in data['partitions'].items():
                part_size = part_data['size']
                part_label = part_data['links']['labels']
                part_uuid = part_data['links']['uuids']
                part_ids = part_data['links']['ids']

                part_dict = {
                    'name': part_name,
                    'size': part_size,
                    'label': part_label,
                    'uuid': part_uuid,
                    'ids': part_ids,
                }

                partitions.append(part_dict)

            device_dict = {
                'name': name,
                'size': size,
                'label': label,
                'uuid': uuid,
                'vendor': vendor,
                'ids': ids,
                'model': model,
                'host': host,
                'partitions': partitions
            }

            device = Device(**device_dict)
            devices.append(device)
        return devices

    def _server_facts(self, results):

        distribution = results['ansible_distribution']
        distribution_version = results['ansible_distribution_version']
        memory_total = results['ansible_memtotal_mb']
        memory_free = results['ansible_memfree_mb']
        hostname = results['ansible_hostname']
        vendor = results['ansible_system_vendor']
        uptime = results['ansible_uptime_seconds']
        kernel = results['ansible_kernel']
        cpu = results['ansible_processor_vcpus']
        json = results['ansible_system']
        space = sum(mount.get('size_total', 0) for mount in results['ansible_mounts'])

        server_dict = {
            'distribution': distribution,
            'distribution_version': distribution_version,
            'memory_total': memory_total,
            'memory_free': memory_free,
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
        Result = collections.namedtuple('Result', ['status', 'host', 'data', 'facts'])

        for host, result in self.results_callback.host_ok.items():
            server_facts = self._server_facts(result._result['ansible_facts'])
            devices_facts = self._desk_facts(result._result['ansible_facts'])
            inventory = Inventory(ip=host, server=server_facts, devices=devices_facts)
            result = Result(status='success', host=host, data=inventory.serialize(), facts=result._result['ansible_facts'])
            results.append(result)

        for host, result in self.results_callback.host_failed.items():
            result = Result(status='faild', host=host, data=result._result['msg'], facts=None)
            results.append(result)

        for host, result in self.results_callback.host_unreachable.items():
            result = Result(status='unreachable', host=host, data=result._result['msg'], facts=None)
            results.append(result)

        return results

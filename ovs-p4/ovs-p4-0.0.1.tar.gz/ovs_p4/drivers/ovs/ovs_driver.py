import subprocess
import logging
from ovs_p4.drivers.driver import P4TargetDriver

from exceptions import *

from ovs_p4.engine.utils.util import make_entries_data

from lib import *

LOG = logging.getLogger(__name__)

FILEPATH_TEMPLATE = '/tmp/p4-device-config-%s'

ACTION_ID_LEN = 4

class OvsDriver(P4TargetDriver):

    def __init__(self):
        # FIXME: hardcoded
        self.bridge = 'br0'

    def load_config(self, pipeline_id, config):
        LOG.info("Loading filter program to Open vSwitch...")
        try:
            file_path = FILEPATH_TEMPLATE % pipeline_id
            with open(file_path, "w") as file:
                file.write(config)
        except Exception as e:
            LOG.error("Loading filter prog failed. Error: %s" % e.message)
            raise LoadFilterProgException(e.message)

        cmd = ['sudo', 'ovs-ofctl', 'load-bpf-prog', self.bridge, str(pipeline_id), file_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()

        if proc.returncode == 1:
            LOG.error("Loading filter prog failed. Error: %s" % error)
            raise LoadFilterProgException(error)
        LOG.info("Loading filter prog succeeded.")

    def action_id_to_bytes(self, action_id):
        return [int(action_id >> i & 0xff) for i in (24, 16, 8, 0)]

    def add_table_entry(self, pipeline_id, map_id, match, action, **kwargs):
        LOG.info("Updating BPF map of filter program...")
        value_size = kwargs['max_action_size'] # the size of map's value equals the size of the longest action params
        key_bytes = convert_to_bytes(match)
        params_bytes = convert_to_bytes(action[1])
        action_id_bytes = self.action_id_to_bytes(action[0])
        cmd = ['sudo', 'ovs-ofctl', 'update-bpf-map', self.bridge, str(pipeline_id), str(map_id), 'key']
        cmd.extend(str(e) for e in key_bytes[::-1])
        cmd.append('value')

        # The value follows a standard format:
        #  [ActionID bytes]   [Action Params bytes]
        #   \___32_b____ /     \__max_bitwidth_b__/
        cmd.extend(str(e) for e in action_id_bytes[::-1])
        # fill ActionID with zero bytes
        for i in range(0, ACTION_ID_LEN - len(action_id_bytes)):
            cmd.append('0')
        if params_bytes:
            cmd.extend(str(e) for e in params_bytes[::-1])
        # fill Action Params with zero bytes
        for i in range(0, bitwidthToBytes(value_size) - len(params_bytes)):
            cmd.append('0')
        LOG.info("Invoking OVS command: %s", ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()

        if proc.returncode == 1:
            LOG.error("Updating BPF map of filter program failed. Error: %s" % error)
            raise Exception()
        LOG.info("Updating BPF map of filter program succeeded.")

    def get_table_entries(self, pipeline_id, map_id, p4info):
        entries = []
        LOG.info("Dumping BPF map of filter program %s..." % pipeline_id)
        cmd = ['sudo', 'ovs-ofctl', 'dump-bpf-map', self.bridge, str(pipeline_id), str(map_id)]
        LOG.info("Invoking OVS command: %s", ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        print output

        for key, value in self.get_next_map_entry(output):
            match_keys = self.to_p4_match_keys(map_id, key, p4info)
            action_name, action_params = self.to_p4_action_data(map_id, value, p4info)
            entry = make_entries_data(match_keys=match_keys,
                                      action_name=action_name,
                                      action_params=action_params)
            entries.append(entry)

        if proc.returncode == 1:
            LOG.error("Dumping BPF map of filter program %s failed. Error: %s" % (pipeline_id, error))
            raise Exception()

        LOG.debug("Dump of BPF map:\n%s" % output)

        LOG.info("Dumping BPF map of filter program %s succeeded." % pipeline_id)
        return entries

    def get_next_map_entry(self, output):
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if 'Key:' in lines[i-1]:
                key = line
                value = lines[i+2]
                yield key, value

    def to_p4_match_keys(self, map_id, key, p4info):
        key = key.split(' ')[::-1]
        match_keys = dict()
        table = p4info.tables[map_id]
        print table
        offset = 0
        for mf in table.match_fields:
            print mf
            match_keys[mf.name] = ''.join(convert_from_bytes(key[offset:bitwidthToBytes(mf.bitwidth)]))
            offset += mf.bitwidth
        print match_keys
        return match_keys

    def to_p4_action_data(self, map_id, value, p4info):
        value = value.split(' ')[::-1]
        action_id_str = ''.join(convert_from_bytes(value[len(value) - ACTION_ID_LEN:]))
        action_id = int(action_id_str.encode('hex'), 16)

        action_name = self.get_action_name_by_ovs_id(p4info, map_id, action_id)
        action_params = self.get_action_params(p4info, action_name, param_data=value[:ACTION_ID_LEN])

        return action_name, action_params

    def get_action_name_by_ovs_id(self, p4info, map_id, id):
        helper = P4InfoHelper(p4info)
        table = p4info.tables[map_id]
        for idx, a in enumerate(table.action_refs):
            action = helper.get('actions', id=a.id)
            if idx == id:
                return action.preamble.name

    def get_action_params(self, p4info, action_name, param_data):
        params = dict()
        for act in p4info.actions:
            if act.preamble.name == action_name:
                offset = 0
                for p in act.params:
                    params[p.name] = ''.join(convert_from_bytes(param_data[0:bitwidthToBytes(p.bitwidth)]))
                    offset += p.bitwidth
        return params

    def do_map_update(self):
        pass

    def do_map_dump(self):
        pass

    def do_map_delete(self):
        pass
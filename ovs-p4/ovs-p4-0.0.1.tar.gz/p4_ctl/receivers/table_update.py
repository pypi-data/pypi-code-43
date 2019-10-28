from p4.v1 import p4runtime_pb2
from lib import P4InfoHelper


class TableUpdate:

    def __init__(self, client, args):
        self.client = client
        self.args = args

    def parse_match_value(self, match_field, match_field_value):
        match_type = match_field.match_type
        if match_type == match_field.EXACT:
            return match_field_value
        elif match_type == match_field.LPM:
            try:
                prefix, length = match_field_value.split("/")
            except ValueError:
                raise Exception("Wrong LPM format")
            return prefix, length
        elif match_type == match_field.TERNARY:
            try:
                key, mask = match_field_value.split("&&&")
            except ValueError:
                raise Exception(
                    "Invalid ternary value {}, use '&&&' to separate key and "
                    "mask".format(match_field_value))
            return key, mask
        elif match_type == match_field.VALID:
            return match_field_value
        elif match_type == match_field.RANGE:
            try:
                start, end = match_field_value.split("->")
            except ValueError:
                raise Exception(
                    "Invalid range value {}, use '->' to separate range start "
                    "and range end".format(match_field_value))

            return start, end
        else:
            raise Exception("Not known match type!")

    def table_update(self):
        pipeline_id = self.args.pipeline_id
        entry = self.args.entry
        p4info_file_path = self.args.p4info_path
        table_name = entry[0]

        p4info = P4InfoHelper.read_from_file(p4info_file_path)
        p4info_helper = P4InfoHelper(p4info)

        nr_of_keys = len(entry) - 2
        table = p4info_helper.get("tables", table_name)

        if len(table.match_fields) != nr_of_keys:
            print "Found %s match key pair(s) but expected %s" % (nr_of_keys, len(table.match_fields))

        match_fields = self.parse_match_fields(table, entry)
        if not match_fields:
            return

        action_name, action_param_values = self.parse_action(entry)
        action_params = self.parse_action_params(action_name, action_param_values, p4info_helper)

        table_entry = p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            action_name=action_name,
            action_params=action_params)

        self.client.write_table_entry(pipeline_id, table_entry, p4runtime_pb2.Update.MODIFY)

        print "Table entry added"

    def parse_action_params(self, action_name, action_param_values, p4info_helper):
        action_params = {}
        action = p4info_helper.get("actions", action_name)
        for index, action_param in enumerate(action.params):
            action_params[action_param.name] = action_param_values[index]
        return action_params

    def parse_action(self, entry):
        action_string = entry[len(entry) - 1]
        action = action_string.split("=")[1]
        action_tmp = action.split(":")
        action_name = action_tmp[0]
        if len(action_tmp) == 1:
            return action_name, {}
        else:
            action_params = action_tmp[1].split(",")
            return action_name, action_params

    def parse_match_fields(self, table, entry):
        match_field_values = entry[1: len(entry) - 1]
        for index, mf in enumerate(match_field_values):
            match_field_values[index] = mf.split("=")

        match_fields = {}
        for index, mf in enumerate(table.match_fields):
            match_field_parsed = match_field_values[index]
            if match_field_parsed[0] != mf.name:
                raise Exception("Match field %s does not exist. Expected %s" % (match_field_parsed[0], mf.name))
            match_fields[mf.name] = self.parse_match_value(mf, match_field_parsed[1])

        return match_fields


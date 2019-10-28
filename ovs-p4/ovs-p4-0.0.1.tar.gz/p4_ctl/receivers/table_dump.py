from lib import *


class TableDump:

    def __init__(self, client, args):
        self.client = client
        self.args = args

    def table_dump(self):
        p4info_file_path = self.args.p4info_path
        pipeline_id = self.args.pipeline_id
        table_name = self.args.table

        p4info = P4InfoHelper.read_from_file(p4info_file_path)
        p4info_helper = P4InfoHelper(p4info)

        table_id = p4info_helper.get_tables_id(table_name)
        table_entries = self.client.read_table_entries(pipeline_id, table_id)

        self.print_table_entries(p4info_helper, table_entries)

    def print_table_entries(self, p4info_helper, table_entries):
        for response in table_entries:
            for entity in response.entities:
                entry = entity.table_entry
                table_id = entry.table_id
                table_name = p4info_helper.get_name('tables', id=table_id)
                print "\n{0:20} {1}".format("Table entry of:", table_name)

                match_fields = []
                for match_field in iter(entry.match):
                    p4info_match_field = p4info_helper.get_match_field(table_name, id=match_field.field_id)
                    match_type = p4info_match_field.MatchType.DESCRIPTOR.values_by_number[
                        p4info_match_field.match_type].name
                    match_value = p4info_helper.get_match_field_value(match_field)
                    bytes_array = convert_to_bytes(match_value)
                    match_field_str = "%s-%s" % (match_type, ':'.join([str(x) for x in bytes_array]))
                    match_fields.append(match_field_str)
                print "{0:20} {1}".format("match key:", ' '.join(match_fields))

                action_name = p4info_helper.get_name("actions", entry.action.action.action_id)

                print "{0:20} {1}".format("action:", action_name)
                action_params = []
                for param in entry.action.action.params:
                    bytes_array = convert_to_bytes(param.value)
                    action_params.append(':'.join([str(x) for x in bytes_array]))
                print "{0:20} {1}".format("action params:", ' '.join(action_params))
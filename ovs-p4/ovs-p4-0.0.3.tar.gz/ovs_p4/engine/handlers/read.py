import logging

from abstract import AbstractService
from lib import P4InfoHelper

LOG = logging.getLogger(__name__)


class ReadService(AbstractService):

    def __init__(self, ovs_driver, db_conn):
        AbstractService.__init__(self, ovs_driver, db_conn)

    def handle(self, **kwargs):
        pipeline_id = kwargs['pipeline_id']
        LOG.info("Reading table entries of pipeline %s..." % pipeline_id)

        for entity in kwargs['entities']:
            if not entity.table_entry:
                raise NotImplementedError('Write operation is supported only for TableEntry!')
            entries = []
            for e in self.read_table_entry(pipeline_id, entity.table_entry):
                LOG.debug("Table entry read:\n%s" % e)
                entries.append(e)
            return entries

    def read_table_entry(self, pipeline_id, table_entry):
        p4info = self.db_conn.get_p4info(pipeline_id)
        helper = P4InfoHelper(p4info)
        table_id = table_entry.table_id
        table_ids = []
        if table_id == 0:
            table_ids.extend(helper.get_all_tables_ids())
        else:
            table_ids.append(table_id)

        for tbl_id in table_ids:
            table_name = helper.get_name('tables', tbl_id)
            map_id = helper.get_table_elem_id(table_name)
            table_entries_data = self.ovs_driver.get_table_entries(pipeline_id=pipeline_id,
                                                                   map_id=map_id,
                                                                   p4info=p4info)

            for entry in table_entries_data:
                print entry
                table_entry = helper.buildTableEntry(
                    table_name=table_name,
                    match_fields=entry['match_keys'],
                    action_name=entry['action_name'],
                    action_params=entry['action_params']
                )
                yield table_entry

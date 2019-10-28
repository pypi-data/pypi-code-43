import logging

from abstract import AbstractService

from p4.v1.p4runtime_pb2 import Update

from lib import P4InfoHelper

LOG = logging.getLogger(__name__)


class WriteService(AbstractService):

    def __init__(self, ovs_driver, db_conn):
        AbstractService.__init__(self, ovs_driver, db_conn)

    def handle(self, **kwargs):
        pipeline_id = kwargs['pipeline_id']
        for update in kwargs['updates']:
            LOG.info("Received WriteRequest for entry: %s" % update.entity)
            if not update.entity.table_entry:
                raise NotImplementedError('Write operation is supported only for TableEntry!')
            if update.type == Update.INSERT or update.type == Update.MODIFY:
                self.add_table_entry(pipeline_id, update.entity.table_entry)
            elif update.type == Update.DELETE:
                self.delete_table_entry(pipeline_id, update.entity.table_entry)

    def add_table_entry(self, pipeline_id, table_entry):
        LOG.info("Adding table entry...")
        p4info = self.db_conn.get_p4info(pipeline_id)
        helper = P4InfoHelper(p4info)
        table_id = table_entry.table_id

        table_name = helper.get_name('tables', table_id)
        keys = []
        for m in table_entry.match:
            print helper.get_match_field_name(table_name, m.field_id),
            mf = helper.get_match_field(table_name, id=m.field_id)
            value = helper.get_match_field_value(m)
            print '%r' % value,
            keys.append(value)

        params = []
        action = table_entry.action.action
        action_name = helper.get_name('actions', action.action_id)
        print '-> %s' % action_name,
        for p in action.params:
            action_param = helper.get_action_param(action_name, id=p.param_id)

            print '%s %r' % (action_param.name, p.value)
            params.append(p.value)
        action = (helper.get_action_elem_id(table_name, action.action_id), params)
        LOG.debug("Installing Table Entry for Table ID %s" % helper.get_table_elem_id(table_name))

        max_params_bitwidth = helper.get_max_action_param_bitwidth(table_name)

        self.ovs_driver.add_table_entry(pipeline_id=pipeline_id,
                                        map_id=helper.get_table_elem_id(table_name),
                                        match=keys,
                                        action=action,
                                        max_action_size=max_params_bitwidth)

    def delete_table_entry(self, pipeline_id, table_entry):
        LOG.info("Deleting table entry...")
        raise NotImplementedError('Implement it!')
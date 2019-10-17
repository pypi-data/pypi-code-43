# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function


class ItemClean(object):
    # __slots__ = ['method', 'url', 'params', 'data', 'headers',
    # 'proxy', 'cookies', 'info', 'timeout', 'max_retry']

    def __init__(self, item_cl, item_config_list, task_name):
        self.database_src_name = item_cl.get('database_src_name', None)
        self.database_src_host = item_cl.get('database_src_host', None)
        self.database_src_port = item_cl.get('database_src_port', None)
        self.database_src_user = item_cl.get('database_src_user', None)
        self.database_src_password = item_cl.get('database_src_password', None)

        self.database_tgt_name = item_cl.get('database_tgt_name', None)
        self.database_tgt_host = item_cl.get('database_tgt_host', None)
        self.database_tgt_port = item_cl.get('database_tgt_port', None)
        self.database_tgt_user = item_cl.get('database_tgt_user', None)
        self.database_tgt_password = item_cl.get('database_tgt_password', None)
        self.database_tgt_table_name = item_cl.get('database_tgt_table_name', None)

        self.item_config_list = item_config_list
        self.task_name = task_name

    def json(self):
        js = dict(
            database_src_host=self.database_src_host,
            database_src_name=self.database_src_name,
            database_src_port=self.database_src_port,
            database_src_user=self.database_src_user,
            database_src_password=self.database_src_password,

            database_tgt_name=self.database_tgt_name,
            database_tgt_host=self.database_tgt_host,
            database_tgt_port=self.database_tgt_port,
            database_tgt_user=self.database_tgt_user,
            database_tgt_password=self.database_tgt_password,
            database_tgt_table_name=self.database_tgt_table_name,

            item_config_list=self.item_config_list,
            task_name=self.task_name
        )
        return js

# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.node import node
from suanpan.arguments.auto import ProxyArg


class DataFrame(ProxyArg):
    MAPPING = {
        "data": "suanpan.storage.arguments.Csv",
        "table": "suanpan.dw.arguments.Table",
    }

    def __init__(self, key, table, partition, *args, **kwargs):
        port = node.get(table) or node.get(key)
        if not port:
            raise Exception(
                "No such {}: {}".format(self.name, ",".join([key, table, partition]))
            )
        kwargs.setdefault(self.TYPE_KEY, port.type)
        kwargs.update(key=key, table=table, partition=partition)
        super(DataFrame, self).__init__(*args, **kwargs)

# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.arguments import Arg, String
from suanpan.dw import dw


class DWArg(Arg):
    def getOutputTmpValue(self, *args):
        return "_".join(args)


class Table(DWArg):
    def __init__(self, key, table, partition, **kwargs):
        kwargs.setdefault("required", False)
        super(Table, self).__init__(key)
        self.table = String(key=table, required=kwargs["required"])
        self.partition = String(key=partition)

    @property
    def isSet(self):
        return True

    def addParserArguments(self, parser):
        self.table.addParserArguments(parser)
        self.partition.addParserArguments(parser)

    def load(self, args):
        self.table.load(args)
        self.partition.load(args)
        if self.table.value:
            self.value = {"table": self.table.value, "partition": self.partition.value}

    def format(self, context):
        if self.value:
            self.value = dw.readTable(self.table.value, self.partition.value)
        return self.value

    def save(self, context, result):
        data = result.value
        dw.writeTable(self.table.value, data)
        self.logSaved(self.table.value)
        return self.value

    def getOutputTmpArg(self, *args):
        value = self.getOutputTmpValue(  # pylint: disable=assignment-from-no-return
            *args
        )
        return ("--{}".format(self.table.key), value) if value is not None else tuple()

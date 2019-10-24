# coding=utf-8
from __future__ import absolute_import, print_function

import base64
import copy
import itertools
import re
from collections import namedtuple

from lostc import collection as lcc

from suanpan import g
from suanpan.log import logger
from suanpan.objects import HasName
from suanpan.utils import json

Param = namedtuple("Param", ["uuid", "name", "type"])
Port = namedtuple("Port", ["uuid", "name", "type", "subtype"])


class BaseNode(HasName):
    NODE_INFO_KEY = "SP_NODE_INFO"
    DEFAULT_NODE_INFO = {"info": {}, "inputs": {}, "outputs": {}, "params": {}}

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(BaseNode, self).__init__()
        self._node = self.load()

    def __getattr__(self, key):
        value = self._getPort(key) if re.match(r"(in|out)\d+", key) else self.get(key)
        if value is None:
            raise Exception("{} not contains {}".format(self.name, key))
        return value

    def _getPort(self, key):
        return lcc.first(
            itertools.chain(self.inputs, self.outputs), lambda i: i.uuid == key
        )

    def get(self, key, default=None):
        for _, collection in self._node.items():
            if isinstance(collection, dict):
                if key in collection:
                    return collection[key]
        return default

    @property
    def info(self):
        return self._node["info"]

    @property
    def inputs(self):
        return self._node["inputs"].values()

    @property
    def ins(self):
        return self._node["inputs"].values()

    @property
    def outputs(self):
        return self._node["outputs"].values()

    @property
    def outs(self):
        return self._node["outputs"].values()

    @property
    def params(self):
        return self._node["params"].values()

    def loadFromEnv(self):
        nodeInfoBase64 = g.nodeInfo
        logger.debug("{}(Base64)='{}'".format(self.NODE_INFO_KEY, nodeInfoBase64))
        nodeInfoString = base64.b64decode(nodeInfoBase64).decode()
        nodeInfo = json.loads(nodeInfoString)
        return nodeInfo

    def formatNodeInfo(self, nodeInfo):
        inputs = {
            name: Port(**port) for name, port in nodeInfo.get("inputs", {}).items()
        }
        outputs = {
            name: Port(**port) for name, port in nodeInfo.get("outputs", {}).items()
        }
        params = {
            name: Param(**param) for name, param in nodeInfo.get("params", {}).items()
        }
        return {"inputs": inputs, "outputs": outputs, "params": params}

    def defaultNodeInfo(self):
        return copy.deepcopy(self.DEFAULT_NODE_INFO)

    def _updateInfo(self, *infos):
        result = self.defaultNodeInfo()
        keys = result.keys()
        for info in infos:
            for key in keys:
                result[key].update(info.get(key, {}))
        return result

    def load(self):
        return self._updateInfo(self.formatNodeInfo(self.loadFromEnv()))

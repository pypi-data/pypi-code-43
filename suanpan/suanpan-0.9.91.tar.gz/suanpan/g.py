# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan.objects import Context

g = Context(
    userId=os.environ.get("SP_USER_ID"),
    appId=os.environ.get("SP_APP_ID"),
    nodeId=os.environ.get("SP_NODE_ID"),
    nodeGroup=os.environ.get("SP_NODE_GROUP", "default"),
    host=os.environ.get("SP_HOST"),
    hostTls=os.environ.get("SP_HOST_TLS") in ("true", "True"),
    apiHost=os.environ.get("SP_API_HOST"),
    apiHostTls=os.environ.get("SP_API_HOST_TLS") in ("true", "True"),
    affinity=os.environ.get("SP_AFFINITY"),
    userIdHeaderField=os.environ.get("SP_USER_ID_HEADER_FIELD", "x-sp-user-id")
)

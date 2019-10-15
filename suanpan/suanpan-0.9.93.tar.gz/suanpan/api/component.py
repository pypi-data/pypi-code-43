# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import api


def listComponents(limit=9999):
    return api.affinity.post("/component/list", json={"limit": limit})["list"]


def shareComponent(componentId, userId, name):
    return api.affinity.post("/component/share", json={"id": componentId, "targetUserId": userId, "name": name})

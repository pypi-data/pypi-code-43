# -*- coding: utf-8 -*-

import json
from lbdrabbit import LbdFuncConfig

__lbd_func_config__ = LbdFuncConfig(
    lbd_func_timeout=30,
)

users = {
    "uid_1": {"user_id": "uid_1", "name": "Alice"},
    "uid_2": {"user_id": "uid_2", "name": "Bob"},
    "uid_3": {"user_id": "uid_3", "name": "Cathy"},
}


def get(event, context):
    return {
        "status_code": "200",
        "body": json.dumps(list(users.values()))
    }


def post(event, context):
    print(event)
    return {
        "status_code": "200",
        "body": json.dumps({"post_data": event})
    }

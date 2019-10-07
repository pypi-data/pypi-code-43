# -*- coding: utf-8 -*-

import json


def handler(event, context):
    print(event)
    return {
        "status_code": "200",
        "body": json.dumps(event["a"] + event["b"])
    }

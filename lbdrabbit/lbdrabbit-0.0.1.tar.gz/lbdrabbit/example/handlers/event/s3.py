# -*- coding: utf-8 -*-

import json
from lbdrabbit import LbdFuncConfig


def handler(event, context):
    print(event)
    return {
        "status_code": "200",
        "body": json.dumps(event)
    }


handler.__lbd_func_config__ = LbdFuncConfig()
handler.__lbd_func_config__.s3_event_bucket_yes = True
handler.__lbd_func_config__.s3_event_bucket_basename = "data-store"
handler.__lbd_func_config__.s3_event_lbd_config_list = [
    LbdFuncConfig.S3EventLambdaConfig(
        event=LbdFuncConfig.S3EventLambdaConfig.EventEnum.created_put,
    )
]

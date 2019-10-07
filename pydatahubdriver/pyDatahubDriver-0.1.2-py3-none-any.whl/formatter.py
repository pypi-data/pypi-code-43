"""This module contains the data formatter"""

import json

def _json_response(res):
    str_response = res.read().decode('utf-8')

    if res.status < 200 or res.status >= 300:
        raise ValueError('Error {} from server:{}', res.status, str_response)

    obj_res = json.loads(str_response)
    if isinstance(obj_res, str):
        raise ValueError(obj_res)

    return obj_res
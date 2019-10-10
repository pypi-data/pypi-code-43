# -*- coding: future_fstrings -*-
import json


def get_body(data, jsondump=True):
    if isinstance(data, list):
        if jsondump:
            out = [json.dumps(d) for d in data]
        else:
            out = data
        body = "\n".join(out).encode("utf-8")
    else:
        body = json.dumps(data).encode("utf-8")
    return body



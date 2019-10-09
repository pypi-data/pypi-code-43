import os
from typing import Tuple, Optional, List, Mapping

import requests


def apply_async(host: str,
                api: str,
                auth: Tuple = None,
                args: Optional[List] = None,
                kwargs: Optional[Mapping] = None,
                queue: str = ''):
    is_valid = lambda x: x[0] in ('args', 'kwargs', 'queue') and x[1]
    url = os.path.join(host, 'api/task/async-apply', api)
    parameter = dict(filter(is_valid, locals().items()))
    send_task = requests.post(url, json=parameter, auth=auth) if auth else requests.post(url, json=parameter)
    if not send_task.ok:
        raise SystemError('request url {} failed, flower not work'.format(url))
    return send_task.json()

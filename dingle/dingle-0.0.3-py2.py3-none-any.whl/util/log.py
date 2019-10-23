# -*- coding: utf-8 -*-
'''
Logging utilities.
'''
import json
import logging
from .conf import get_config

logger = logging.getLogger('dingle')


def json_log(obj, desc=None):
    config = get_config()
    message = desc if desc else ''
    if config.get('verbose2'):
        message = '[%s]\n' % message if message else message
        message = '%s%s' % (message, json.dumps(obj, ensure_ascii=False, indent=2))
        logger.info(message)
    elif config.get('verbose'):
        message = '[%s] ' % message if message else message
        message = '%s%s' % (message, json.dumps(obj, ensure_ascii=False))
        logger.info(message)
    else:
        pass

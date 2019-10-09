import os
from spacemakerlog3 import log
import logging

log.set_level_external('warn')
log.set_level(os.getenv('LOG_LEVEL', 'debug'))
log.set_format(os.getenv('LOG_FORMAT', 'json'))

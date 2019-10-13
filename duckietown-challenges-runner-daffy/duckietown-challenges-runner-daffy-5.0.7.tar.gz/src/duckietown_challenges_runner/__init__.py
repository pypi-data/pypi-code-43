# coding=utf-8
__version__ = "5.0.7"
import logging
import sys

logging.basicConfig()
dclogger = logging.getLogger("dt-challenges-runner")
dclogger.setLevel(logging.DEBUG)

dclogger.info("dt-challenges-runner %s" % __version__)
msg = f"Default encoding {sys.getdefaultencoding()}"
dclogger.debug(msg)

from requests import __version__ as requests_version

dclogger.info("using: requests %s" % requests_version)
from docker import __version__ as docker_version

dclogger.info("using: docker-py %s" % docker_version)

from .exceptions import *

from .runner import dt_challenges_evaluator

from .runner_local import runner_local_main

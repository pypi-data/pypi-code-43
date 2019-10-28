#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from .results import Results
from .solr_error import SolrError
from .solr import Solr
from .solr_cloud import SolrCloud
from .zk import ZooKeeper
from .solr_core_admin import SolrCoreAdmin

__desc__ = "Python3 client for Apache Solr"
__project__ = "py3Solr"
__author__ = "wbq813"
__author_email__ = "wbq813@foxmail.com"
__version__ = "0.1.0"


def get_version():
    return __version__


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logger = logging.getLogger(__project__)
h = NullHandler()
logger.addHandler(h)

# For debugging...
if os.environ.get("DEBUG_PYSOLR", "").lower() in ("true", "1"):
    logger.setLevel(logging.DEBUG)
    stream = logging.StreamHandler()
    logger.addHandler(stream)

__all__ = ["Solr", "SolrCloud", "ZooKeeper", "SolrCoreAdmin", "Results", "SolrError"]

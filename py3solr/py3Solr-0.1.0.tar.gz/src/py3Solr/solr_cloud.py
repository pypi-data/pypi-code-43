#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import logging
import time

import requests

from .solr import Solr
from .solr_error import SolrError

logger = logging.getLogger(__name__)


class SolrCloud(Solr):
    def __init__(
            self,
            zookeeper,
            collection,
            decoder=None,
            timeout=60,
            retry_count=5,
            retry_timeout=0.2,
            auth=None,
            verify=True,
            *args,
            **kwargs
    ):
        url = zookeeper.getRandomURL(collection)
        self.auth = auth
        self.collection = collection
        self.retry_count = retry_count
        self.retry_timeout = retry_timeout
        self.verify = verify
        self.zookeeper = zookeeper

        super(SolrCloud, self).__init__(
            url,
            decoder=decoder,
            timeout=timeout,
            auth=self.auth,
            verify=self.verify,
            *args,
            **kwargs
        )

    def _send_request(self, method, path="", body=None, headers=None, files=None):
        for retry_number in range(0, self.retry_count):
            try:
                self.url = self.zookeeper.getRandomURL(self.collection)
                return Solr._send_request(self, method, path, body, headers, files)
            except (SolrError, requests.exceptions.RequestException):
                logger.exception(
                    "%s %s failed on retry %s, will retry after %0.1fs",
                    method,
                    self.url,
                    retry_number,
                    self.retry_timeout,
                )
                time.sleep(self.retry_timeout)

        raise SolrError(
            "Request %s %s failed after %d attempts" % (method, path, self.retry_count)
        )

    def _update(self, *args, **kwargs):
        self.url = self.zookeeper.getLeaderURL(self.collection)
        logger.debug("Using leader URL: %s", self.url)
        return Solr._update(self, *args, **kwargs)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""
import time
import logging
import requests
import requests.exceptions
from cdumay_http_client import errors

logger = logging.getLogger(__name__)


class HttpClient(object):
    """HttpClient"""

    def __init__(
            self, server, timeout=10, headers=None, username=None,
            password=None, ssl_verify=True):
        self.server = server
        self.timeout = timeout
        self.headers = headers or dict()
        self.auth = (username, password) if username and password else None
        self.ssl_verify = ssl_verify

    def __repr__(self):
        return 'Connection: %s' % self.server

    def _request_wrapper(self, **kwargs):
        return requests.request(**kwargs)

    # noinspection PyMethodMayBeStatic
    def _format_data(self, data):
        return data

    # noinspection PyMethodMayBeStatic
    def _parse_response(self, response):
        return response.text

    def do_request(self, method, path, params=None, data=None, headers=None,
                   timeout=None, parse_output=True, stream=False, **kwargs):
        req_url = ''.join([self.server.rstrip('/'), path])
        req_headers = headers or dict()
        req_headers.update(self.headers)
        request_start_time = time.time()
        extra = dict(url=req_url, server=self.server, method=method)

        logger.debug("[{}] - {}".format(method, req_url))
        try:
            response = self._request_wrapper(
                method=method, url=req_url, params=params,
                data=self._format_data(data), auth=self.auth,
                headers=req_headers, stream=stream,
                timeout=timeout or self.timeout, verify=self.ssl_verify,
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            raise errors.InternalServerError(
                message=getattr(e, 'message', "Internal Server Error"),
                extra=extra
            )
        finally:
            execution_time = time.time() - request_start_time

        if response is None:
            raise errors.MisdirectedRequest(extra=extra)

        content = getattr(response, 'content', "")
        logger.info(
            "[{}] - {} - {}: {} - {}s".format(
                method, req_url, response.status_code,
                len(content), round(execution_time, 3)
            ),
            extra=dict(
                exec_time=execution_time, status_code=response.status_code,
                content_lenght=len(content), **extra
            )
        )
        if response.status_code >= 300:
            raise errors.from_response(response, req_url)

        if parse_output is True:
            return self._parse_response(response)
        else:
            return response

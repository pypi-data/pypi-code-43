#!/usr/bin/env python
# Copyright (c) 2019 Radware LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# @author: Leon Meguira, Radware

import platform
import logging
import urllib3
import json as _json
import ssl
from urllib3.exceptions import ProxyError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)


def is_py3():
    ver = platform.python_version_tuple()
    return int(ver[0]) >= 3


class Request(object):
    def __init__(self, method=None, url=None, headers=None, data=None, params=None,
                 auth=None, json=None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.data = data or []
        self.json = json
        self.params = params or {}
        self.auth = auth

    def prepare(self):
        p = PreparedRequest()
        p.prepare(
            method=self.method,
            url=self.url,
            headers=self.headers,
            data=self.data,
            json=self.json,
            params=self.params,
        )
        return p

    def __str__(self):
        return str(self.__dict__)


class Response(object):
    def __init__(self):
        self._content = None
        self.status = None
        self.headers = dict()
        self.url = None
        self.reason = None
        self.request = None

    @property
    def content(self):
        if self._content:
            return self._content.decode('utf-8')


    @property
    def raw_content(self):
        return self._content

    def json(self):
        return _json.loads(self._content)

    @property
    def ok(self):
        if not self.status:
            return False
        if int(self.status) > 400:
            return False
        # try:
        #     response = self.json()
        #     if 'code' in response and response['code'] > 400:
        #         return False
        # except ValueError:
        #     pass
        return True

    def __str__(self):
        return str(self.__dict__)


class PreparedRequest(object):
    def __init__(self):
        self.method = None
        self.url = None
        self.headers = None
        self.body = None

    def prepare(self, method=None, url=None, headers=None, data=None, params=None, json=None):
        self.prepare_method(method)
        self.prepare_url(url, params)
        self.prepare_headers(headers)
        self.prepare_body(data, json)

    def prepare_url(self, url, params):
        self.url = url

    def prepare_method(self, method):
        self.method = method
        if self.method:
            self.method = self.method.upper()

    def prepare_headers(self, headers):
        self.headers = {}
        if headers:
            for k, v in headers.items():
                self.headers[k] = v

    def prepare_body(self, data, json=None):
        body = None
        content_type = None

        if not data and json is not None:
            self.headers['Content-Type'] = 'application/json'
            body = _json.dumps(json)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')

        if data:
            body = data
            content_type = None

        if content_type and 'content-type' not in self.headers:
            self.headers['Content-Type'] = content_type

        self.body = body


class RestSession(object):

    def __init__(self, cert_verify=True, block=False, max_connection=1, http_proxy_url=None, https_proxy_url=None):
        if not cert_verify:
            self.http = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE, block=block, maxsize=max_connection)
        else:
            self.http = urllib3.PoolManager(block=block)
        if http_proxy_url:
            self.http_proxy = urllib3.ProxyManager(http_proxy_url)
        else:
            self.http_proxy = None
        if https_proxy_url:
            self.https_proxy_url = urllib3.ProxyManager(https_proxy_url)
        else:
            self.https_proxy = None

        self.headers = self.default_headers()
        self.verify = True
        self.params = {}
        self.timeout = 30

        self.server = None
        self.user = None
        self.password = None
        self.server_port = None
        self.auth_provider = None

    def default_headers(self):
        return {
            'connection': 'keep-alive',
            'accept': '*/*',
        }

    def _normalize_headers(self, headers):
        result = {}
        result.update(dict((k.lower(), v) for k, v in headers))

        if is_py3():
            temp_headers = {}
            for name, value in headers:
                name = name.lower()
                if name in temp_headers:
                    temp_headers[name] = ', '.join((temp_headers[name], value))
                else:
                    temp_headers[name] = value
            result.update(temp_headers)
        return result

    def prepare_request(self, request):
        headers = self.headers.copy()
        params = self.params.copy()

        if request.headers is not None:
            headers.update(request.headers)
        if request.params is not None:
            params.update(request.params)

        prepared = PreparedRequest()
        prepared.prepare(
            method=request.method,
            url=request.url,
            data=request.data,
            json=request.json,
            headers=headers,
            params=params,
        )
        return prepared

    def request(self, method, url, params=None, data=None, headers=None, auth=None,
                timeout=None, verify=None, json=None, user=None, password=None, **kw):

        request = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=json,
            data=data or {},
            params=params or {},
            auth=auth
        )
        kwargs = dict(
            timeout=timeout,
            verify=verify,
            user=user,
            password=password
        )
        kwargs.update(kw)
        prepared = self.prepare_request(request)
        return self.send(prepared, **kwargs)

    def send(self, request, **kwargs):
        response = Response()
        if 'user' in kwargs and 'password' in kwargs:
            auth = urllib3.make_headers(basic_auth="{0}:{1}".format(kwargs.get('user'),
                                                                    kwargs.get('password')))['authorization']
            request.headers.update(dict(authorization=auth))

        params = dict(
            url=request.url,
            method=request.method,
            headers=request.headers,
            retries=False
        )
        if kwargs['timeout'] is None:
            params.update(timeout=self.timeout)
        else:
            params.update(timeout=kwargs['timeout'])

        if request.body:
            params.update(body=request.body)
        if 'fields' in kwargs:
            params.update(fields=kwargs.get('fields'))

        try:
            if 'use_http_proxy' in kwargs and kwargs.get('use_http_proxy'):
                if self.http_proxy is None:
                    raise ProxyError('no http proxy server specified')
                result = self.http_proxy.request(**params)
            elif 'use_https_proxy' in kwargs and kwargs.get('use_https_proxy'):
                if self.https_proxy is None:
                    raise ProxyError('no https proxy server specified')
                result = self.https_proxy.request(**params)
            else:
                result = self.http.request(**params)
            response._content = result.data
            response.status = result.status
            response.url = result.geturl()
            response.msg = "OK (%s bytes)" % result.headers.get('Content-Length', 'unknown')
            response.headers = self._normalize_headers(result.headers.items())
            response.request = request

        except urllib3.exceptions.HTTPError as e:
            try:
                if hasattr(e, 'read'):
                    response._content = e.read()
            except AttributeError:
                response._content = ''

            response.request = request
            if hasattr(e, 'reason'):
                response.reason = e.reason
            else:
                response.reason = e

        return response

    def delete(self, url, json=None, **kwargs):
        return self.request('DELETE', url, json=json, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)



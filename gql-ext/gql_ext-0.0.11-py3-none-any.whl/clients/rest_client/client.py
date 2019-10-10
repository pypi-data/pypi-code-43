import logging
import re
from functools import partial
from typing import Mapping, Union, List, Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from gql_ext.exceptions import BadRequestError
from gql_ext.resolvers import EndpointABC

logger = logging.getLogger()

__all__ = ('get', 'post', 'patch', 'delete', 'HttpApi', 'ApiRequest')


class RequestOptions:
    def __init__(self, method: str, url: str, *,
                 query_params: Union[Mapping, None] = None,
                 json_body: Union[Mapping, None] = None,
                 headers: Union[Mapping, None] = None):
        self.method = method
        self.url = url
        self.params = query_params
        self.json = json_body
        self.headers = headers

    def get_options(self) -> Mapping:
        return {'method': self.method, 'url': self.url, 'json': self.json, 'params': self.params,
                'headers': self.headers}


class ApiRequest(EndpointABC):
    BODY_METHODS = ('POST', 'PATCH', 'PUT')
    NO_BODY_METHODS = ('GET', 'DELETE', 'HEAD')

    def __init__(self, path_template: str, *,
                 base_url: Union[str, None] = None,
                 method: Union[str, None] = None,
                 session: Union[ClientSession, None] = None):
        self.base_url = base_url
        self.path_template = path_template
        self.method = method
        self.path_params = None
        self.session = session
        self.proxy_headers = []

    def __get__(self, instance, owner):
        if instance is None:
            return self
        self.session = instance.session
        self.base_url = instance.base_url
        self.proxy_headers = instance.proxy_headers
        return self

    async def __call__(self, **kwargs):
        return await self.request(**kwargs)

    async def request(self, **kwargs) -> Mapping:
        if not self.method:
            raise NotImplementedError('Not known method')
        if not self.session:
            self.session = ClientSession(raise_for_status=True)

        request_options = self.get_request_options(**kwargs)
        async with self.session.request(**request_options.get_options()) as resp:
            return await resp.json()

    def get_request_options(self, **kwargs) -> RequestOptions:
        self.path_params = self.get_path_params(self.path_template, **kwargs)
        path = self.format_path(self.path_template, self.path_params)
        url = urljoin(self.base_url, path)
        headers = self.get_headers(kwargs.pop('headers', None))

        query_params = self.get_query_params(kwargs)
        json_body = self.get_json_body(kwargs)

        return RequestOptions(self.method, url, json_body=json_body, query_params=query_params, headers=headers)

    def get_headers(self, headers) -> Union[dict, None]:
        res = {}
        if not headers:
            return
        for header_name, header_value in headers.items():
            if header_name in self.proxy_headers:
                res[header_name] = header_value
        return res

    @staticmethod
    def get_path_params(path: str, **kwargs) -> Union[List, None]:
        path_params = list()
        params_name = re.findall(r'{(\w*)}', path)
        for p_name in params_name:
            if p_name not in kwargs.keys():
                raise Exception('You must declare all path params')
            path_value = kwargs.get(p_name)
            if isinstance(path_value, (list, tuple)):
                path_value = path_value[0]
            path_params.append((p_name, path_value))
        return path_params

    @staticmethod
    def format_path(path_template: str, path_params: Union[None, List]) -> str:
        formatted_path = path_template
        for k, v in path_params:
            formatted_path = formatted_path.replace('{%s}' % k, str(v))
        return formatted_path

    def get_json_body(self, params: Union[Mapping, None] = None) -> Union[Mapping, None]:
        if self.method in self.BODY_METHODS:
            return {key: val for key, val in params.items() if key not in self.path_params}

    def get_query_params(self, params: Union[Mapping, None] = None) -> Union[List, None]:
        if self.method not in self.NO_BODY_METHODS:
            return
        _params = list()

        for k, v in params.items():
            if (k, v) not in self.path_params:
                if isinstance(v, bool):
                    self.add_param(_params, k, str(v).lower())
                elif isinstance(v, (tuple, list)):
                    if len(v) == 0:
                        raise BadRequestError(f'length of iterable arg {k} is 0')
                    for val in v:
                        self.add_param(_params, k, val)
                else:
                    self.add_param(_params, k, v)

        return _params

    @staticmethod
    def add_param(params: List, key: Any, value: Any):
        if (key, value) not in params:
            params.append((key, value))


class HttpApi:
    @classmethod
    async def create(cls, url: str, session: Union[ClientSession, None] = None,
                     proxy_headers: Union[List, None] = None):
        if session is None:
            session = ClientSession(raise_for_status=True)
        return cls(url, session, proxy_headers)

    def __init__(self, base_url: str, session: ClientSession, proxy_headers: Union[List, None]):
        self.base_url = base_url
        self.session = session
        self.proxy_headers = proxy_headers or []


get = partial(ApiRequest, method='GET')
post = partial(ApiRequest, method='POST')
delete = partial(ApiRequest, method='DELETE')
patch = partial(ApiRequest, method='PATCH')

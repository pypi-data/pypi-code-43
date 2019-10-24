from .config import config
from .exceptions import InvalidEndpoint, HttpError, InvalidResponse, NetworkError, APIError
from requests import Session, RequestException
from urllib.parse import urlencode
import keyword
import json


ENDPOINTS = {
    'desarrollo': 'http://dev.api.virtualname.net/v1/',
    'produccion': 'https://api.virtualname.net/v1/',
}

TIMEOUT = 180


class Client(object):
    """
    Comment
    """
    def __init__(self, endpoint=None, application_key=None, config_file=None,
                 timeout=TIMEOUT):
        # Load a custom config file
        if config_file is not None:
            config.read(config_file)

        # Load endpoint
        if endpoint is None:
            endpoint = config.get('default', 'endpoint')

        try:
            self._endpoint = ENDPOINTS[endpoint]
        except KeyError:
            raise InvalidEndpoint("Unknow endpoint %s. Valid endpoints: %s",
                                  endpoint, ENDPOINTS.keys())

        # Load keys
        if application_key is None:
            application_key = config.get(endpoint, 'application_key')

        self._application_key = application_key

        # request session to reuse request connection
        self._session = Session()

        # Override default timeout
        self._timeout = timeout

    def _canonicalize_kwargs(self, kwargs):
        arguments = {}

        for k, v in kwargs.items():
            if k[0] == '_' and k[1:] in keyword.kwlist:
                k  = k[1:]
            arguments[k] = v

        return arguments

    def _prepare_query_string(self, kwargs):
        arguments = {}

        for k, v in kwargs.items():
            if isinstance(v, bool):
                v = str(v).lower()
            arguments[k] = v

        return urlencode(arguments)

    def get(self, _target, _need_auth=True, **kwargs):
        """
        'GET' :py:func:`Client.call` wrapper.

        Query string parameters can be set either directly in ``_targe`` or as
        keywork arguments. If an argument collides with a Python reserved
        keyword, prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        :param string _need_auth: If True, send authentication headers. This is
        the default
        """
        if kwargs:
            kwargs = self._canonicalize_kwargs(kwargs)
            query_string = self._prepare_query_string(kwargs)
            if '?' in _target:
                _target = '%s&%s' % (_target, query_string)
            else:
                _target = '%s?%s' % (_target, query_string)

        return self.call('GET', _target, None, _need_auth)

    def call(self, method, path, data=None, need_auth=True):
        try:
            result = self.raw_call(method=method, path=path, data=data, need_auth=need_auth)
        except RequestException as error:
            raise HttpError("Low HTTP request failed error", error)

        status = result.status_code

        try:
            json_result = result.json()
        except ValueError as error:
            raise InvalidResponse("Failed to decode API response", error)

        if status >= 100 and status < 300:
            return json_result
        elif status == 0:
            raise NetworkError()
        else:
            raise APIError(json_result.get('message'), response=result)

    def raw_call(self, method, path, data=None, need_auth=True):
        body = ''

        target = self._endpoint + path
        headers = {
            'X-TCpanel-Token': self._application_key
        }

        if data is not None:
            headers['Content-type'] = 'application/json'
            body = json.dumps(data)

        if need_auth:
            if not self._application_key:
                raise InvalidEndpoint("Invalid  ApplicationKey '%s'" %
                                      self._application_key)

        return self._session.request(method, target, headers=headers,
                                     data=body, timeout=self._timeout)

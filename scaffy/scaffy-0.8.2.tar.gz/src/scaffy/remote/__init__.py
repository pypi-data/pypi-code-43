# -*- coding: utf-8 -*-
""" API client for scaffyhub. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from datetime import datetime
from functools import wraps
from os.path import exists

# 3rd party imports
import requests

# local imports
from scaffy.config import settings
from scaffy.core import shell


def print_api_errors(fn):
    """ A handy decorator to print out all uncaught ApiErrors. """
    @wraps(fn)
    def wrapper(*args, **kw):   # pylint: disable=missing-docstring
        try:
            return fn(*args, **kw)
        except ApiError as ex:
            shell.cprint('^31{}^0'.format(str(ex)))

    return wrapper


class ApiError(RuntimeError):
    """ Base class for all API client. errors. """
    def __init__(self, response, message=None):
        if message is None:
            try:
                message = '[{code}] {detail}'.format(
                    code=response.status_code,
                    detail=json.dumps(response.json()['detail'], indent=2)
                )
            except Exception:
                message = '[{code}] Unknown error:\n{body}'.format(
                    code=response.status_code,
                    body=response.text
                )

        super(ApiError, self).__init__(message)
        self.response = response


class ApiClientSectionBase(object):
    """ Base class for API sections.

    To avoid having a huge client class with all possible API calls the API
    client is divided into sections. The sections are setup/initialized in the
    `Client._init_api_sections()` method and if you create new ones you should
    subclass this class and add a new section there.
    """
    def __init__(self, client):
        self.api = client


class Client(object):
    """ scaffyhub API client. """

    class BackendNotFound(RuntimeError):
        """ Raised when the client can't connect to the backend."""
        pass

    def __init__(self, backend_url=None):
        self.backend_url = backend_url or self._discover_backend()
        self._token = None
        self._init_api_sections()

    def _discover_backend(self):
        backends = settings.BACKENDS

        for backend in backends:
            if backend.endswith('/'):
                backend = backend[:-1]

            try:
                url = backend + '/api/ping'
                r = requests.get(url)
                if r.status_code == 200:
                    return backend
            except:
                pass
        raise Client.BackendNotFound("Backend unreachable: {}".format(backends))

    def _init_api_sections(self):
        """ Initialize API section.

        For more information, see `ApiClientSectionBase`
        """
        from .scaffold import ScaffoldApi

        self.scaffold = ScaffoldApi(self)

    @property
    def token(self):
        """ Get the authorization token.

        If it doesn't have a cached value it will try to read it from
        `settings.CREDENTIALS_PATH`.
        """
        if self._token is None:
            if exists(settings.CREDENTIALS_PATH):
                with open(settings.CREDENTIALS_PATH) as fp:
                    self._token = fp.read()

        return self._token

    @token.setter
    def token(self, token):
        self._token = token

        with open(settings.CREDENTIALS_PATH, 'w') as fp:
            fp.write(token)

    def url(self, relative_url):
        """ Get the full URL from the API relative url."""
        if not relative_url.startswith('/'):
            relative_url = '/' + relative_url

        return self.backend_url + relative_url

    def login(self, username, password):
        """ Login to scaffyhub

        On successful login it will store the authorization token for later use.

        :param str username:
            scaffyhub username
        :param str password:
            scaffyhub password
        """
        r = requests.post(self.url('/api/user/login'), json={
            'username': username,
            'password': password
        })

        if r.status_code != 200:
            raise ApiError(r)

        self.token = r.json()['jwt_token']

    def get(self, url, params=None, headers=None, **kw):
        """ Proxy for requests.get that handles auth. """
        if self.token is not None:
            headers = headers or {}
            headers['Authorization'] = 'JWT ' + self.token

        return requests.get(self.url(url), params, headers=headers, **kw)

    def post(self, url, data=None, headers=None, **kw):
        """ Proxy for requests.post that handles auth. """
        if self.token is not None:
            headers = headers or {}
            headers['Authorization'] = 'JWT ' + self.token

        return requests.post(self.url(url), json=data, headers=headers, **kw)

    def put(self, url, data=None, headers=None, **kw):
        """ Proxy for requests.put that handles auth. """
        if self.token is not None:
            headers = headers or {}
            headers['Authorization'] = 'JWT ' + self.token

        return requests.put(self.url(url), json=data, headers=headers, **kw)

    def delete(self, url, headers=None, **kw):
        """ Proxy for requests.delete that handles auth. """
        if self.token is not None:
            headers = headers or {}
            headers['Authorization'] = 'JWT ' + self.token

        return requests.delete(self.url(url), headers=headers, **kw)

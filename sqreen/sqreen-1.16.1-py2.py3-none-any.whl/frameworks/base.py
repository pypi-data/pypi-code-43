# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base Request class
"""

import logging
import traceback
import uuid
from collections import defaultdict

from ..config import CONFIG
from ..remote_exception import traceback_formatter
from ..utils import to_unicode_safe
from .ip_utils import get_real_user_ip

LOGGER = logging.getLogger(__name__)


# Header name that we need to sends back on attack in order to compute the
# real user ip
CLIENT_IP_HEADERS = (
    "HTTP_X_FORWARDED_FOR",
    "X_FORWARDED_FOR",
    "HTTP_X_REAL_IP",
    "HTTP_CLIENT_IP",
    "HTTP_X_FORWARDED",
    "HTTP_X_CLUSTER_CLIENT_IP",
    "HTTP_FORWARDED_FOR",
    "HTTP_FORWARDED",
    "HTTP_VIA",
    "REMOTE_ADDR",
)


class BaseRequest(object):

    DEBUG_MODE = None

    def __init__(self, storage=None):
        self._flat_request_params = None
        self._flat_request_params_keys = None
        self._request_headers = None
        self.request_id = uuid.uuid4().hex
        self.storage = storage

        if CONFIG["IP_HEADER"]:
            self._client_ip_headers = [
                "HTTP_%s" % CONFIG["IP_HEADER"].upper().replace("-", "_")
            ] + list(CLIENT_IP_HEADERS)
        else:
            self._client_ip_headers = CLIENT_IP_HEADERS

    @property
    def remote_addr(self):
        raise NotImplementedError

    @property
    def hostname(self):
        raise NotImplementedError

    @property
    def method(self):
        raise NotImplementedError

    @property
    def referer(self):
        raise NotImplementedError

    @property
    def client_user_agent(self):
        raise NotImplementedError

    @property
    def path(self):
        raise NotImplementedError

    @property
    def scheme(self):
        raise NotImplementedError

    @property
    def server_port(self):
        raise NotImplementedError

    @property
    def remote_port(self):
        raise NotImplementedError

    @property
    def raw_headers(self):
        raise NotImplementedError

    @property
    def form_params(self):
        raise NotImplementedError

    @property
    def query_params(self):
        raise NotImplementedError

    @property
    def view_params(self):
        raise NotImplementedError

    @property
    def json_params(self):
        raise NotImplementedError

    @property
    def cookies_params(self):
        raise NotImplementedError

    @property
    def body(self):
        raise NotImplementedError

    @property
    def request_payload(self):
        """ Returns current request payload with the backend expected field
        name. All fields should be serializable to JSON.
        """
        return {
            "rid": self.request_id,
            "remote_ip": self.remote_addr,
            "client_ip": self.client_ip,
            "host": self.hostname,
            "verb": self.method,
            "referer": self.referer,
            "user_agent": self.client_user_agent,
            "path": self.path,
            "scheme": self.scheme,
            "port": self.server_port,
            "remote_port": self.remote_port,
        }

    @property
    def request_params(self):
        """ Returns all the inputs that are controllable by the user.
        All fields should be serializable to JSON.
        """
        return {
            "form": self.form_params,
            "query": self.query_params,
            "other": self.view_params,
            "json": self.json_params,
            "cookies": self.cookies_params,
        }

    @property
    def request_params_list(self):
        """ Returns all the inputs that are controllable by the user without
        keys. All fields should be serializable to JSON.
        """
        return [
            self.form_params,
            self.query_params,
            self.view_params,
            self.json_params,
            self.cookies_params,
        ]

    @property
    def request_params_filtered(self):
        """ Returns all the inputs that are controllable by the user without cookies.
        This is based on the Ruby reference implementation.
        """
        ret = self.request_params
        ret.pop("cookies", None)
        return ret

    def _flatten_request_params(self):
        """ Flatten the request params to compute the values and keys for
        quick access
        """
        iteration = 0
        max_iterations = 100

        values = set()
        keys = set()
        remaining_iterables = list(self.request_params_list)

        while len(remaining_iterables) != 0:

            iteration += 1
            # If we have a very big or nested iterable, returns False
            if iteration >= max_iterations:
                break

            iterable_value = remaining_iterables.pop(0)

            # If we get an iterable, add it to the list of remaining
            if isinstance(iterable_value, dict):
                dict_values = iterable_value.values()

                # Be sure to not extend with an empty dict, faster check
                if len(dict_values) > 0:
                    remaining_iterables.extend(list(dict_values))

                dict_keys = iterable_value.keys()

                if len(dict_keys) > 0:
                    keys.update(dict_keys)

            elif isinstance(iterable_value, list):
                # Be sure to not extend with an empty list, faster check
                if len(iterable_value) > 0:
                    remaining_iterables.extend(iterable_value)
            else:
                values.add(iterable_value)

        self._flat_request_params = values
        self._flat_request_params_keys = keys

    @property
    def flat_request_params(self):
        """ Return only the request params values for all request params
        """
        if self._flat_request_params is None:
            self._flatten_request_params()

        return self._flat_request_params

    @property
    def flat_request_params_keys(self):
        """ Return only the request params names for all request params
        """
        if self._flat_request_params_keys is None:
            self._flatten_request_params()
        return self._flat_request_params_keys

    def params_contains(self, param):
        """ Return True if the parameter given in input is present in the
        request inputs.
        """
        return param in self.flat_request_params

    @property
    def flat_cookies_values(self):
        """ Return the cookies values
        """
        return list(self.cookies_params.values())

    @property
    def flat_cookies_keys(self):
        """ Return the cookies values
        """
        return list(self.cookies_params.keys())

    @property
    def request_headers(self):
        if self._request_headers is None:
            self._request_headers = defaultdict(lambda: None)

            for key, value in self.raw_headers.items():
                key = to_unicode_safe(key)
                value = to_unicode_safe(value)
                if not key.startswith("HTTP_"):
                    if key == "CONTENT_LENGTH" and value:
                        # Some WSGI implementations set CONTENT_LENGTH to
                        # an empty string when not set in the HTTP request.
                        # We actually prefer to consider the header not set.
                        pass
                    elif key != "CONTENT_TYPE":
                        continue
                self._request_headers[key] = value
        return self._request_headers

    @property
    def content_type(self):
        return self.get_raw_header("CONTENT_TYPE")

    @property
    def content_length(self):
        try:
            return int(self.get_raw_header("CONTENT_LENGTH"))
        except ValueError:
            return None

    @property
    def flat_headers_values(self):
        return list(self.request_headers.values())

    @property
    def flat_headers_keys(self):
        return list(self.request_headers.keys())

    @property
    def caller(self):
        return traceback.format_stack()

    @property
    def raw_caller(self):
        return traceback_formatter(traceback.extract_stack())

    @property
    def client_ip(self):
        """String formatted client IP address."""
        ip = self.raw_client_ip
        if ip is not None:
            return to_unicode_safe(ip)

    @property
    def raw_client_ip(self):
        """Client IP address."""
        return get_real_user_ip(self.remote_addr, *self.iter_client_ips())

    def get_raw_header(self, name, default=None):
        """ Get a specific raw header."""
        return to_unicode_safe(self.raw_headers.get(name, default))

    def iter_client_ips(self):
        """Yield the client IPs set in raw headers."""
        for header_name in self._client_ip_headers:
            value = self.get_raw_header(header_name)
            if value:
                yield value

    def get_client_ips_headers(self):
        """ Return raw headers that can be used to find the real client ip
        """
        raw_headers = []
        for header_name in self._client_ip_headers:
            value = self.get_raw_header(header_name)
            if value:
                raw_headers.append([header_name, value])

        return raw_headers


class BaseResponse(object):

    @property
    def status_code(self):
        raise NotImplementedError

    @property
    def content_type(self):
        raise NotImplementedError

    def content_length(self):
        raise NotImplementedError

    @property
    def response_payload(self):
        """Returns the response information understood by the backend.
        """
        return {
            "status": self.status_code,
            "content_type": self.content_type,
            "content_length": self.content_length,
        }

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import re

from flask import g, request
from functools import wraps
from cdumay_rest_client.client import RESTClient
from cdumay_http_client.errors import Unauthorized, Forbidden

from flask_graylog_bundle import GraylogExt, MESSAGE_MAP

logger = logging.getLogger(__name__)


class GraylogAuth(GraylogExt):
    def login_required(self, func):
        """When applied to a view function, any unauthenticated requests will
        be denied. Authenticated requests do NOT require membership from a
        specific group.

        :param func: The view function to decorate.
        """

        @wraps(func)
        def wrapped(*args, **kwargs):
            """wrapped"""
            user_info = self.load_user_info()
            if not user_info:
                return self.authenticate()
            return func(*args, **kwargs)

        return wrapped

    @property
    def username(self):
        """Return the user name or None if a user is not logged in"""

        if not self.load_user_info():
            return None

        return g.user['username']

    @staticmethod
    def authenticate():
        """Sends a 401 response"""
        logger.error(MESSAGE_MAP["AuthenticationFailed"])
        raise Unauthorized(
            message=MESSAGE_MAP["AuthenticationFailed"],
            extra=dict(msgid="AuthenticationFailed")
        )

    def load_user_info(self):
        """If a new authorization is requested, check Graylog authentication on
         /roles using the given credentials. Forbidden is expected. This process
         allow to login using tokens.

        :return: result of GET /users/{username} on success else None
        """
        if getattr(g, 'user', None):
            return g.user

        auth = request.authorization
        if not auth:
            g.user = None
            return g.user

        client = RESTClient(
            server=self.app.config['GRAYLOG_API_URL'], **auth
        )
        try:
            client.do_request(method="GET", path="/roles")

        except Unauthorized:
            self.authenticate()
        except Forbidden as exc:
            match = re.search("User \[(.*?)\] not authorized", exc.message)
            if match:
                g.user = client.do_request(
                    method="GET",
                    path="/users/%s" % match.group(1)
                )
                return g.user

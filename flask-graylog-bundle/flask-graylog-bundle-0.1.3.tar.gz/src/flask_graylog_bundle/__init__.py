#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from flask.blueprints import Blueprint

MESSAGE_MAP = dict(
    AuthenticationFailed="Authentication failed",
    PasswordNull="Password cannot be null"
)


class GraylogExt(object):
    def __init__(self, app=None):
        self.app = None
        self.blueprint = None
        self.blueprint_setup = None
        self._client = None

        if app is not None:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if isinstance(app, Blueprint):
            app.record(self._deferred_blueprint_init)
        else:
            self._init_app(app)

    def _deferred_blueprint_init(self, setup_state):
        self._init_app(setup_state.app)

    @staticmethod
    def _init_app(app):
        """"""
        app.config.setdefault('GRAYLOG_API_URL', 'http://127.0.0.1:12900')
        app.config.setdefault('GRAYLOG_API_USERNAME', 'test')
        app.config.setdefault('GRAYLOG_API_PASSWORD', 'test')

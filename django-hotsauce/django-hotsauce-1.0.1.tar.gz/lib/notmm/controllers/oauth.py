#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)
from notmm.controllers.base import BaseController, sessionmanager
from notmm.controllers.wsgi import WSGIController
#from wsgi_oauth2.client import google_client

__all__ = ['GoogleController',]

class GoogleController(BaseController):
    scope = 'email'

    #oauth_client_class = google_client
    oauth_client_version = "2.0"
    oauth_client_debug = True

    def __init__(self, client, secret, **kwargs):
        super(GoogleController, self).__init__()
        self._client = client
        self._secret = secret
        self._login_path = kwargs['login_path']
        if self.oauth_client_debug:
            log.debug(self._client)   
    
    def application(self, environ, start_response):
        with sessionmanager(environ):
            req = self.request_class(environ)
            #self.init_request(req)
            app = self._client.wsgi_middleware(self, secret=self._secret, 
                login_path=self._login_path)
        return app(environ, start_response)


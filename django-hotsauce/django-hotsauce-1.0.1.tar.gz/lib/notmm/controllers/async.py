#!/usr/bin/env python
# -*- coding: utf-8 -*-
# For experimental use only... Require CPython > 3.4
"""AsyncIOController API Version 0.8.2

"""

import sys
import logging
import asyncio
from asyncio import get_event_loop
from notmm.controllers.wsgi import WSGIController
from notmm.controllers.base import request, sessionmanager

log = logging.getLogger('asyncio')
log.setLevel(logging.DEBUG)


class AsyncIOController(WSGIController):
    def __init__(self, settings=None, executor=None, loop=None
        ):
        super(AsyncIOController, self).__init__(settings)

    def get_response(self, request=None, method='GET', data={}):
        return super(AsyncIOController, self).get_response(request)
    
    @asyncio.coroutine
    def application(self, environ, start_response):
        with sessionmanager(environ):
            request.environ.update(environ)
            response = self.get_response(request=request)
        return response(environ, start_response)
    
    @asyncio.coroutine
    def __call__(self, environ, start_response):
        return self.application(environ, start_response)

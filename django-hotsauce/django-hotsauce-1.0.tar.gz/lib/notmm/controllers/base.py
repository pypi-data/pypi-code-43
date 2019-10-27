#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""BaseController CPython API Version 1.0 revision 0

Python extension module to implement MVC-style "controllers"
for Django and WSGI type apps. In short, ``BaseController`` derived
extensions are request handlers resolving a ``path_url`` string
to a matching ``view function``. The response handler (view function)
then resolve the appropriate HTTP response to the client.

TODO:
-Better module-level documentation (work-in-progress)
-Compatibility with mod_wsgi (Apache2) (YMMV...)
-Change all prints by log() hooks (work-in-progress)
-use signals to log messages from pubsub like BUS

Define and document the internal request handling stages when
using native Django views (WSGIHandler):
 __init__,         # application init -> self.init_request(env)
 init_request,     # setup the environment -> self.process_request(req)
 process_request,  # handle the request -> self.locals.request = req
 get_response,     # resolve request [PATH_INFO] -> response_callback
 application,      # response stage 2 [WSGI] -> response_callback(env, start_response)
"""

import sys
import os
import urllib
import logging
import traceback

from contextlib import contextmanager
from notmm.utils.wsgilib import (
    HTTPRequest, 
    HTTPResponse,
    #HTTPNotFound,
    #HTTPUnauthorized,
    #HTTPException
    )
from notmm.utils.wsgilib.exc import (
    HTTPNotFound, 
    HTTPUnauthorized, 
    HTTPException
    )

from notmm.utils.django_compat import NoReverseMatch

from werkzeug.local import Local, LocalProxy

RequestClass = HTTPRequest

_local = Local()
#local_manager = LocalManager([_local]) 

__all__ = ('BaseController', 'sessionmanager', 'get_current_request')


@contextmanager
def sessionmanager(request):
    _local.request = request
    yield
    _local.request = None

def get_current_request():
    try:
        return _local.request
    except AttributeError:
        raise TypeError("No request object for this thread")

_request = LocalProxy(lambda: get_current_request())

class BaseController(object):
    debug = False
    settings = None
    request_class = RequestClass
    response_class = HTTPResponse
    _response = None

    def sethandle(self, name, string_or_callable):
        """Adds custom response handlers to a BaseController subclass.
        """

        # If string_or_callable is in the form of "foo.bar.quux",
        # the callable function should be the last part of the
        # string
        handler = None
        if isinstance(string_or_callable, str):
            if string_or_callable.find('.') != -1:
                bits = string_or_callable.rsplit('.', 1)
                m = __import__(bits[0], globals(), locals(), fromlist=[''])
                for component in bits[1:]:
                    if hasattr(m, component):
                        handler = getattr(m, component)
                        break
                    else:
                        #print 'debug: module %s has no such member: %r' % (m, component)
                        continue
        elif callable(string_or_callable):
            handler = string_or_callable
        else:
            raise ValueError("Unexpected string_or_callable type: %r" % \
                type(string_or_callable))

        if not callable(handler) and isinstance(handler, str):
            # Attempt to import it
            # XXX write a native eval_import hook
            if 'debug.config.eval_import_func' in self.app_conf:
                handler_obj = self.app_conf['debug.config.eval_import_func'](handler)
            else:
                raise Exception("fatal error: debug.config.eval_import_func not set!")
        else:
            handler_obj = handler

        # XXX Use staticmethod(func) here, because we want to support the
        # same positional arguments named by this callable
        setattr(self, name, handler_obj)

        return None

    def __call__(self, environ, start_response, exc_info=None):
        # WSGI 1.0 mandates to return a callable object
        #self._environ.update(environ)
        if exc_info is not None:
            # TODO: exc_info verifications
            if self.debug:
                self.logger.debug(exc_info)
            return self.application(environ, start_response, exc_info)
        return self.application(environ, start_response)

    def application(self, environ, start_response):
        """
        Override this to change the default request/response
        handling.

        This method is used for properly returning a WSGI response instance
        by calling ``get_response``.

        The latter does the grunt work of routing the request to the
        proper callable function or class.

        """
        req = self.request_class(environ)

        with sessionmanager(req):
            
            self._request = self.init_request(req)
        
            if self.debug:
                assert _request == self.request, 'Invalid request object!'
                assert _request == get_current_request(), 'Request is not the current one!'
            try:
                self._response = self.get_response(request=self.request)
            except HTTPException:
                #if self.debug:
                #    assert isinstance(self._response, self.response_class), 'wrong response type!'
                return self.handle500(request)
        return self._response(environ, start_response)

    def registerWSGIHandlers(self, d):
        """Register appropriate wsgi callbacks (legacy method
        for backward compat only)"""
        for k, v in d:
            # "register" the callback function as a standard Django view
            # accessible by the controller extension
            self.sethandle(k, v)
        #self.registered = True
        return None
    
    def init_request(self, request):
        """A method to execute before ``process_request``"""
        # put handle404 and handle500 in request.environ
        if hasattr(self, 'handle404'):
            request.environ['django.request.handle404'] = self.handle404
        if hasattr(self, 'handle500'):
            request.environ['django.request.handle500'] = self.handle500
        if hasattr(self, 'settings'):
            request.environ['django.settings'] = self.settings
        return request    

    @property
    def request(self):
        return self._request


    def get_response(self, request, method='GET', data={}):
        """Process ``path_url`` and return a callable function as
        the WSGI ``response`` callback.

        The callback view function is resolved using the built-in
        Django ``RegexURLResolver`` class.

        Returns a callable function (Response) or None if no
        view functions matched.

        See the docs in :notmm.utils.django_compat.RegexURLResolver:
        for details.

        This function may be overrided in custom subclasses to modify
        the response type.
        """
        # Match the location to a view or callable
        #path_info = self.get_path_info(self.environ)
        
        if self.debug:
            assert hasattr(request, 'path_url'), 'something is broken!'
            #assert isinstance(request, self.request_class), 'Unknown request class: %s' % type(request)

        try:
            if self.debug:
                #assert self.request != None, 'invalid request object!'
                self.logger.debug("Resolving path=%r"%request.path_url)

            # If the path doesn't end with a slash, redirect to the same path
            # with an ending slash.
            if (not request.path_url.endswith('/') 
                and self.settings.APPEND_SLASH == True):
                redirect_url = request.path_url + '/'
                return self.handle302(request, location=redirect_url)

            # Resolve the path (endpoint) to a view using legacy Django URL
            # resolver.
            (callback, args, kwargs) = self.resolver.resolve(str(request.path_url))
            if self.debug and self.logger:
                self.logger.debug("callback resolved=%r"%callback)
            # Create the wsgi ``response`` object.
            # If `callback` here is a decorator type we're fuck and it will returns a
            # http request object.
            response = callback(request, *args, **kwargs)
            #self.logger.debug("new response type: %s" % type(response))
        except NoReverseMatch as e:
            # Handle 404 responses with a custom 404 handler.
            self.logger.info('Document not found=%s'%request.path_url)
            if self.debug:
                self.logger.debug(e)
            #handleclienterror(self.request)

            return self.handle404(request)
        except HTTPException:
            if self.debug:
                exc = traceback.format_exc()
                self.logger.debug(exc)
            return self.handle500(request)
        except HTTPUnauthorized as exc:
            if self.debug:
                self.logger.debug("Caught authorization exception!")
                self.logger.debug(exc)
            return self.handle401(request)
        else:
            return response
    
    @property
    def response(self):
        return self._response

    @property
    def user(self):
        return self.request.get_user()

    def _environ_getter(self):
        """ Returns the current WSGI environment instance."""
        return getattr(self, '_environ', {})

    environ = property(_environ_getter)

    def _method_getter(self):
        return self.environ['REQUEST_METHOD']
    method = property(_method_getter)

    def _debug_getter(self):
        """Global debug flag. 
        Set settings.DEBUG to False to disable debugging"""
        return bool(self.settings.DEBUG == True)
    debug = property(_debug_getter)

    def _get_path_info(self, env):
        return str(env.get('PATH_INFO', ''))


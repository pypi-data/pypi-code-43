#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, django
from importlib import import_module

from notmm.controllers.base import BaseController
from notmm.utils.django_settings import SettingsProxy
from notmm.utils.django_compat import get_resolver
from notmm.utils.log import configure_logging

_logger = configure_logging(__name__)

__all__ = ('WSGIController',)

try:
    django.setup()
except:
    _logger.debug("django.setup() is disabled")

class WSGIController(BaseController):

    def __init__(self,
        settings=None,          #Django like settings module (default=$DJANGO_SETTINGS_MODULE)
        #New: dict based configuration (app_conf)
        #TODO document the changes in docs/config.txt
        app_conf={
            #'wsgi.request_class'        : HTTPRequest,     #WSGI Request middleware
            #'wsgi.response_class'       : HTTPResponse,    #WSGI Response middleware
            #'django.urlconf_class'      : None,           #Django URLConf module (default=$ROOT_URLCONF)
            'django.settings_autoload'  : True,          #Set this to False to disable Django settings autoloading (True)
            'logging_conf':None,      #Logging module to handle logging events at run-time  (experimental)
            'logging_instance':_logger,
            'logging.disabled': False,  #Set this to True to disable logging (experimental)
        }):

        """
        Initializes a ``BaseController`` instance for processing
        standard Django view functions and handling basic error conditions.

        Available keyword arguments:

        - ``settings``: Django settings module (optional)
        - ``app_conf``: Dict of configuration options. (optional)
        """
        #super(WSGIController, self).__init__()

        # initialize Django module by importing Django settings
        # if True. (Bool)
        autoload = app_conf.get('django.settings_autoload', True)
        if settings is None:
            self.settings = SettingsProxy(autoload=autoload).get_settings()
        else:
            self.settings = settings

        # Setup basic logging to /var/log/django.log (default)
        logging_disabled = app_conf.get('logging.disabled', False)
        if not logging_disabled:
            self.logger = _logger
        else:
            #print('Logging is disabled!')
            self.logger = None

        # If using legacy autoload mecanism, attempt to register user-specified
        # wsgi callbacks.
        if (autoload and hasattr(self.settings, 'CUSTOM_ERROR_HANDLERS')):
            self.registerWSGIHandlers(self.settings.CUSTOM_ERROR_HANDLERS)

        if (autoload and 'ROOT_URLCONF' in self.settings):
            setattr(self, 'urlconf', self.settings.ROOT_URLCONF)
            setattr(self, 'resolver', get_resolver(self.urlconf, self.settings))
            if not hasattr(self.resolver, '_urlconf_module'):
                self.resolver._urlconf_module = import_module(self.urlconf)
        else:
            self.resolver = None
            self.urlconf = None
        
        # sanity checks 
        if self.debug:
            assert self.urlconf != None, 'urlconf instance cannot be None!'
            assert self.resolver != None, 'resolver instance cannot be None!'

        # Do something with app_conf here
        self.app_conf = app_conf


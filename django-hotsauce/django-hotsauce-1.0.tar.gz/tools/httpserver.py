#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Another stand-alone HTTP server for serving Django apps in pure
WSGI context with the ``wsgiref`` module. 
"""

import os,sys,logging

try:
    import argparse2 as argparse
except ImportError:
    import argparse

    
from notmm.utils.django_settings import LazySettings
from notmm.utils.django_compat import get_callable
from notmm.utils.log import configure_logging
from notmm.utils.pastelib import eval_import
from notmm.http import get_bind_addr, daemonize
from notmm.controllers.wsgi import WSGIController
from notmm.release import VERSION
from wsgi_oauth2.client import GoogleOAuthClient
from wsgi_oauth2.controller import OAuthController    

log = configure_logging('httpserver', enable_syslog=True)

_settings = LazySettings()

# quick and dirty logging dispatcher
_ = lambda x: log.debug(x)

def parse_cmdline(argv):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument('-d', '--debug', action="store_true", \
        help="Enable debugging mode", default=False)
    parser.add_argument('-p', '--port', action="store_true", \
        dest="port",
        help="HTTP port to accept connections. default: 8133",
        default=8133)
    parser.add_argument('-H', '--host', action="store_true", \
        dest="host",
        help="Listening address. default: localhost",
        default="localhost")
    parser.add_argument('-c', '--config', dest="filename",
        default="development.ini", nargs=1, \
        help="Path to a development.ini-like file")
    parser.add_argument('-s', '--ssl', action="store_true", \
        dest="enable_ssl", \
        help="Enable SSL transport mode (not implemented!)")
    parser.add_argument('--disable-auth', action="store_true", \
        dest="disable_auth", \
        help="Disable oauth2 middleware backend", default=True)
    parser.add_argument('--disable-xdserver', action="store_true", \
        dest="disable_xdserver", \
        help="Disable xdserver network database backend", default=False)
    parser.add_argument('--settings', dest="disable_settings", nargs=1, \
        required=False, help="TARGET settings module", default=False)
    # add support for custom PYTHONPATH 
    parser.add_argument('--pythonpath', dest="pythonpath", default=None, \
        required=False)
    
    # show version with --version
    parser.add_argument('--version', dest="version", action="store_true",
            help="Show the current version")

    # app_label hint:
    # ie: satchmo_store.wsgi.application
    parser.add_argument('--wsgi-app', dest="app_label",  
        required=True, help="WSGI callable to launch.")
    
    options = parser.parse_args(args=argv[1:])
    return options

def main(argv):
    options = parse_cmdline(sys.argv)

    if options.version:
        # print the current release and exit
        print("Django-hotsauce %s" % VERSION)
        sys.exit(0)

    if options.pythonpath is not None:
        for path in options.pythonpath.split(':'):
            sys.path.insert(0, path)

    # A INET4 address to bind to for listening for HTTP connections 
    bind_addr = (options.host, options.port)

    if _settings.DEBUG: 
        #_('WSGIController class=%s' % repr(WSGIHandlerClass))
        _("%d settings found in module=%s" % (_settings.count(), repr(_settings)))
        _("Server address: %r" % repr(bind_addr))

    wsgi_app = get_callable(options.app_label) # app.wsgi.callback
    print wsgi_app
    
    if options.disable_auth is not True:

        client = GoogleOAuthClient(
            _settings.OAUTH2_CLIENT_ID,
            access_token=_settings.OAUTH2_ACCESS_TOKEN,
            scope=_settings.OAUTH2_SCOPE, 
            redirect_url=_settings.OAUTH2_REDIRECT_URL,
            )
        if client is not None:

            wsgi_app = OAuthController(
                client=client,
                secret=_settings.SECRET_KEY, 
                login_path=_settings.OAUTH2_LOGIN_URL)
            _("OAuth2 middleware enabled class=%r"% type(wsgi_app))
    else:
        _("OAuth2 middleware disabled.")
    
    daemonize(wsgi_app, bind_addr)

if __name__ == "__main__":
    #assert len(sys.argv) >= 2, 'usage: runserver.py host:port' 
    main(argv=sys.argv)


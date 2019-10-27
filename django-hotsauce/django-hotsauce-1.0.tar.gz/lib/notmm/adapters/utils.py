#!/usr/bin/env python
# -*- coding: utf-8 -*-
from notmm.controllers.wsgi import WSGIController
from notmm.utils.django_settings import LazySettings
from wsgi_oauth2 import client

# init the django settings subsystem
_settings = LazySettings()

__all__ = ['make_app']

def make_app(controller=WSGIController, enable_oauth=False, enable_syslog=False,
    logging_disabled=False, autoload=True):
    
    if enable_syslog and not logging_disabled:
        from notmm.utils.log import configure_logging
        configure_logging('django.hotsauce', enable_syslog=True)

    if not enable_oauth:
        wsgi_app = controller()
    else:
        google_client = client.GoogleClient(
            _settings.OAUTH2_CLIENT_ID,
            access_token=_settings.OAUTH2_ACCESS_TOKEN,
            scope=_settings.OAUTH2_SCOPE, 
            redirect_url=_settings.OAUTH2_REDIRECT_URL)
        
        # see wsgi_oauth2.controller.OAuthController
        wsgi_app = google_client.wsgi_middleware(
            client=google_client,
            secret=_settings.SECRET_KEY, 
            login_path=_settings.OAUTH2_LOGIN_URL,
            forbidden_passthrough=_settings.OAUTH2_FORBIDDEN_PASSTHROUGH)
    return wsgi_app

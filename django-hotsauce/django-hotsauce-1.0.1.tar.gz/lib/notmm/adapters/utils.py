#!/usr/bin/env python
# -*- coding: utf-8 -*-
from notmm.controllers.wsgi import WSGIController
from notmm.utils.django_settings import LazySettings
from wsgi_oauth2 import client



__all__ = ['make_app']

def make_app(controller=WSGIController, enable_oauth=False, 
    enable_syslog=False, logging_disabled=False, autoload=True):
    
    # init the django settings subsystem
    settings = LazySettings()
    
    wsgi_app = controller(settings=settings)
    if enable_oauth:
        google_client = client.GoogleClient(
            _settings.OAUTH2_CLIENT_ID,
            access_token=_settings.OAUTH2_ACCESS_TOKEN,
            scope=_settings.OAUTH2_SCOPE, 
            redirect_url=_settings.OAUTH2_REDIRECT_URL)
        # 
        # see wsgi_oauth2.controller.OAuthController
        #wsgi_app = google_client.wsgi_middleware(
        #    client=google_client,
        #    secret=_settings.SECRET_KEY, 
        #    login_path=_settings.OAUTH2_LOGIN_URL,
        #    forbidden_passthrough=_settings.OAUTH2_FORBIDDEN_PASSTHROUGH)
        wsgi_app = OAuthController(wsgi_app, client=google_client)
    return wsgi_app

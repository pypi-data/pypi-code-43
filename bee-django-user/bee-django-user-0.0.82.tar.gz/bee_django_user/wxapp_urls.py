#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import wxapp


urlpatterns = [
    url(r'^login$', wxapp.login),
    url(r'^user/bind$', wxapp.user_bind),
    url(r'^user/unbind$', wxapp.user_unbind),
]

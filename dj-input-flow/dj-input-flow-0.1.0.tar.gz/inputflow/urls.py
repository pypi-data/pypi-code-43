# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views


app_name = 'inputflow'


urlpatterns = [
    url(r'^webhook/(?P<uid>[0-9a-fA-F\-]+)$', views.webhook, name='inputflow-webhook'),
    url(r'^webhook/(?P<uid>[0-9a-fA-F\-]+)/$', views.webhook, name='inputflow-webhook'),
]

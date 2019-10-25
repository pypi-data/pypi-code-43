# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


app_name = 'oauth_clients'
urlpatterns = [
    url(
        regex="^Client/~create/$",
        view=views.ClientCreateView.as_view(),
        name='Client_create',
    ),
    url(
        regex="^Client/(?P<pk>\d+)/~delete/$",
        view=views.ClientDeleteView.as_view(),
        name='Client_delete',
    ),
    url(
        regex="^Client/(?P<pk>\d+)/$",
        view=views.ClientDetailView.as_view(),
        name='Client_detail',
    ),
    url(
        regex="^Client/(?P<pk>\d+)/~update/$",
        view=views.ClientUpdateView.as_view(),
        name='Client_update',
    ),
    url(
        regex="^Client/$",
        view=views.ClientListView.as_view(),
        name='Client_list',
    ),
	url(
        regex="^AccessToken/~create/$",
        view=views.AccessTokenCreateView.as_view(),
        name='AccessToken_create',
    ),
    url(
        regex="^AccessToken/(?P<pk>\d+)/~delete/$",
        view=views.AccessTokenDeleteView.as_view(),
        name='AccessToken_delete',
    ),
    url(
        regex="^AccessToken/(?P<pk>\d+)/$",
        view=views.AccessTokenDetailView.as_view(),
        name='AccessToken_detail',
    ),
    url(
        regex="^AccessToken/(?P<pk>\d+)/~update/$",
        view=views.AccessTokenUpdateView.as_view(),
        name='AccessToken_update',
    ),
    url(
        regex="^AccessToken/$",
        view=views.AccessTokenListView.as_view(),
        name='AccessToken_list',
    ),
	]

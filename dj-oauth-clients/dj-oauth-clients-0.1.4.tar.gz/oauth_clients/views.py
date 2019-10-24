# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	Client,
	AccessToken,
)


class ClientCreateView(CreateView):

    model = Client


class ClientDeleteView(DeleteView):

    model = Client


class ClientDetailView(DetailView):

    model = Client


class ClientUpdateView(UpdateView):

    model = Client


class ClientListView(ListView):

    model = Client


class AccessTokenCreateView(CreateView):

    model = AccessToken


class AccessTokenDeleteView(DeleteView):

    model = AccessToken


class AccessTokenDetailView(DetailView):

    model = AccessToken


class AccessTokenUpdateView(UpdateView):

    model = AccessToken


class AccessTokenListView(ListView):

    model = AccessToken


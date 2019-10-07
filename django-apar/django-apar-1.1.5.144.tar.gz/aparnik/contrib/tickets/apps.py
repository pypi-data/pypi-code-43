# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TicketConfig(AppConfig):
    name = 'aparnik.contrib.tickets'
    verbose_name = _('Ticket')

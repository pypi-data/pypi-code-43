# -*- coding: utf-8
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save


class InputGoogleSheetsConfig(AppConfig):
    name = 'inputgooglesheets'
    verbose_name = _("Inputs from Google sheets")

    def ready(self):
        from oauth_clients.models import AccessToken
        pre_save.connect(self.handle_saves_access_token, sender=AccessToken,
            dispatch_uid='0f95231d-2d04-4276-8c0a-20116898e562')

    def handle_saves_access_token(self, sender, **kwargs):
        from .utils import Utils
        instance = kwargs['instance']
        if instance.pk is None:
            Utils.fetch_token_info(instance)

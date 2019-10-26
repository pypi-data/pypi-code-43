# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models
from oauth_clients.models import Client, AccessToken as BaseAccessToken
from inputflow.models import InputSettings


@python_2_unicode_compatible
class Settings(models.Model):
    oauth_client = models.ForeignKey(Client, verbose_name=_("Oauth client"),
        blank=True, null=True, default=None, related_name='google_sheets_clients',
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

    def __str__(self):
        return ugettext("Settings")

class AccessTokenManager(models.Manager):
    def get_queryset(self):
        result = super(AccessTokenManager, self).get_queryset()
        settings = Settings.objects.first()
        if settings is None or settings.oauth_client is None:
            return result.none()
        return result.filter(client=settings.oauth_client)

@python_2_unicode_compatible
class AccessToken(BaseAccessToken):
    objects = AccessTokenManager()

    class Meta:
        verbose_name = _("Access token")
        verbose_name_plural = _("Access tokens")
        proxy = True

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_scope())

    def get_scope(self):
        result = self.scope.split()
        result = [scope.split('/')[-1] for scope in result]
        return ', '.join(result)


@python_2_unicode_compatible
class Spreadsheet(models.Model):
    access_token = models.ForeignKey(AccessToken, verbose_name=_("Access token"),
        related_name='available_google_sheets', on_delete=models.CASCADE)
    url = models.URLField(_("URL"), max_length=500)
    name = models.CharField(_("Name"), max_length=250)
    spreadsheet_name = models.CharField(_("Spreadsheet name"), max_length=250)
    uid = models.CharField(_("UID"), max_length=250)
    sheet_index = models.PositiveIntegerField(_("Sheet index"), blank=True, default=0)
    sheet_name = models.CharField(_("Sheet name"), max_length=250, blank=True, default='')

    omit_first_row = models.BooleanField(_("Omit first row"), blank=True,
        default=True)
    last_imported_row = models.PositiveIntegerField(_("Last imported row"),
        blank=True, null=True, default=None)
    last_imported_date = models.DateTimeField(_("Last imported date"),
        blank=True, null=True, default=None)
    enabled = models.BooleanField(_("Enabled"), blank=True, default=True)
    automatically_imported = models.BooleanField(_("Automatically imported"), blank=True,
        default=True)
    
    input_settings = models.ForeignKey(InputSettings, verbose_name=_("Input settings"),
        blank=True, null=True, default=None, on_delete=models.PROTECT,
        related_name='google_spreadsheets')

    class Meta:
        verbose_name = _("Spredsheet")
        verbose_name_plural = _("Spreadsheets")
        unique_together = [('access_token', 'url'),]

    def __str__(self):
        return self.name

    def reset_importing(self):
        self.last_imported_date = None
        self.last_imported_row = None
        self.save()

    def get_start_row_number(self):
        return 2 if self.omit_first_row else 1

    def get_next_row_number(self):
        if self.last_imported_row is None:
            return self.get_start_row_number()
        return self.last_imported_row + 1

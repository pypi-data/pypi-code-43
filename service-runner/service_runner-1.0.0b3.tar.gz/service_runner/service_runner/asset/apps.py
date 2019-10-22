from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AssetConfig(AppConfig):
    name = 'service_runner.service_runner.asset'
    label = 'asset'
    verbose_name = _('Asset')

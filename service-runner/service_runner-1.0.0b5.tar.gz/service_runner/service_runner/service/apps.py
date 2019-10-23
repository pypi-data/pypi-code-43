from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServiceConfig(AppConfig):
    name = 'service_runner.service_runner.service'
    label = 'service'
    verbose_name = _('Service')

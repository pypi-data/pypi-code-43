from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from service_runner.service_runner.asset.models import Host


# Create your models here.


class ServiceType(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('Name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Service Type')
        verbose_name_plural = _('Service Types')


class ServiceConfig(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('Name'))
    content = models.TextField(verbose_name=_('Content'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime')
    )

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Service Config')
        verbose_name_plural = _('Service Configs')


class Service(models.Model):
    host = models.ForeignKey(
        Host, on_delete=models.CASCADE, verbose_name=_('Host'))
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.Model, verbose_name=_('serviceType'))
    service_config = models.ForeignKey(
        ServiceConfig, on_delete=models.CASCADE, verbose_name=_(
            'serviceConfig')
    )
    port = models.IntegerField(blank=True, null=True, verbose_name=_('Port'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime')
    )

    def __str__(self):
        return '{}_{}'.format(self.host, self.service_type.name)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')

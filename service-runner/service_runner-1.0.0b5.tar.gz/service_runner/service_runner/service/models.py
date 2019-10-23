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


class ServiceTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description'))
    hosts = models.ManyToManyField(Host, verbose_name=_('Hosts'))
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.Model, verbose_name=_('serviceType'))
    port = models.IntegerField(blank=True, null=True, verbose_name=_('Port'))
    valid = models.BooleanField(default=True, verbose_name=_('Valid'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime')
    )

    def __str__(self):
        return '{}_{}'.format(self.name, self.service_type.name)

    class Meta:
        verbose_name = _('Service Task')
        verbose_name_plural = _('Service Tasks')


class ServiceTaskRecord(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, auto_created=True,
                          verbose_name=_('Id'))
    service_task = models.ForeignKey(
        ServiceTask, on_delete=models.CASCADE, verbose_name=_('serviceTask'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime')
    )

    def __str__(self):
        return '{}_{}'.format(self.id, self.service_task)

    class Meta:
        verbose_name = _('Service Task Record')
        verbose_name_plural = _('Service Task Records')


class ServiceTaskResponse(models.Model):
    service_task_record = models.ForeignKey(
        ServiceTaskRecord, on_delete=models.CASCADE, verbose_name=_('serviceTaskRecord'))
    host = models.ForeignKey(
        Host, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Host')
    )
    response = models.TextField(
        blank=True, null=True, verbose_name=_('Response'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime')
    )

    def __str__(self):
        return '{}'.format(self.service_task_record)

    class Meta:
        verbose_name = _('Service Task Response')
        verbose_name_plural = _('Service Task Responses')

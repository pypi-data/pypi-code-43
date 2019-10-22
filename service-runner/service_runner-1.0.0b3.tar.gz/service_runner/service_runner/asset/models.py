from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


class HostGroup(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('Name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Host Group')
        verbose_name_plural = _('Host Groups')


class SshKey(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('Name'))
    ssh_key = models.FileField(upload_to='./ssh_key', verbose_name=_('sshKey'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Ssh Key')
        verbose_name_plural = _('Ssh Keys')


class Host(models.Model):
    SYSTEM_TYPE_CHOICE = (
        ('LINUX', 'LINUX'),
        ('MAC', 'MAC'),
        ('WINDOWS', 'WINDOWS'),
        ('UNIX', 'UNIX')
    )
    STATUS_CHOICE = (
        (0, _('READY')),
        (1, _('ONLINE')),
        (2, _('OFFLINE')),
    )
    ip = models.GenericIPAddressField(
        max_length=255, unique=True, verbose_name=_('ipAddress'))
    host_group = models.ForeignKey(
        HostGroup, on_delete=models.CASCADE, verbose_name=_('hostGroup'))
    ssh_user = models.CharField(max_length=255, verbose_name=_('sshUser'))
    ssh_passwd = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('sshPasswd'))
    ssh_key = models.ForeignKey(
        SshKey, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('sshKey'))
    ssh_port = models.IntegerField(default=22, verbose_name=_('sshPort'))
    system_type = models.CharField(
        max_length=255, choices=SYSTEM_TYPE_CHOICE, verbose_name=_('systemType'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description'))
    status = models.IntegerField(
        default=0, choices=STATUS_CHOICE, verbose_name=_('Status'))
    valid = models.BooleanField(default=True, verbose_name=_('Valid'))
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name=_('createTime'))
    update_time = models.DateTimeField(
        auto_now=True, verbose_name=_('updateTime'))

    def __str__(self):
        return '{}'.format(self.ip)

    class Meta:
        verbose_name = _('Host')
        verbose_name_plural = _('Hosts')

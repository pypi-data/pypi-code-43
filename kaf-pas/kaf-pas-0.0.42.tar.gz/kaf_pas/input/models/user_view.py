import logging

from django.db.models import EmailField
from django.utils.translation import gettext_lazy as _

from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel

logger = logging.getLogger(__name__)


class User_viewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class User_viewManager(AuditManager):

    # @staticmethod
    # def getRecord(record):
    #     res = {}
    #     return res

    def get_queryset(self):
        return User_viewQuerySet(self.model, using=self._db)


class User_view(AuditModel):
    username = CodeField(verbose_name=_('логин'))
    first_name = NameField(verbose_name=_('имя'))
    last_name = NameField(verbose_name=_('фамилия'))
    email = EmailField(verbose_name=_('E-mail'), blank=True, null=True)
    middle_name = NameField(verbose_name=_('отчетво'))
    position_name = NameField(verbose_name=_('должность'))
    location_name = NameField(verbose_name=_('место работы'))

    objects = User_viewManager()

    def __str__(self):
        return f"ID: {self.id} username {self.username}"

    class Meta:
        verbose_name = 'Пользователи'
        db_table = 'user_view'
        managed = False

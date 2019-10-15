import logging

from django.db.models import TextField, CharField

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.models.base_ref import Hierarcy

logger = logging.getLogger(__name__)


class CustomerQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class CustomerManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "inn": record.inn,
            "kpp": record.kpp,
            "name": record.name,
            "long_name": record.long_name,
            "full_name": record.full_name,
            "description": record.description,
            "parent_id": record.parent.id if record.parent else None,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db)


class Customer(Hierarcy):
    inn = CodeField(verbose_name="ИНН", max_length=12, db_index=True, null=True, blank=True)
    kpp = CodeField(verbose_name="КПП", max_length=9, db_index=True, null=True, blank=True)
    name = CharField(verbose_name="Наименование", max_length=255, db_index=True)
    long_name = TextField(verbose_name="Полное наименование", null=True, blank=True)
    description = TextField(verbose_name="Описание", null=True, blank=True)

    objects = CustomerManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Клиент'

import logging

from isc_common.fields.code_field import CodeField
from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.base_ref import BaseRef

logger = logging.getLogger(__name__)


class StatusQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class StatusManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "code": record.code,
            "name": record.name,
            "description": record.description,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return StatusQuerySet(self.model, using=self._db)


class Status(BaseRef):
    objects = StatusManager()

    def get_status(self, code):
        try:
            return self.objects.get(code=code)
        except Status.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Статусы'

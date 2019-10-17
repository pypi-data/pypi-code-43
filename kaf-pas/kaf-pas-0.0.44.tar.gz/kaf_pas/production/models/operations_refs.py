import logging

from django.db.models import Model

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Operations_refsQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Operations_refsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {}
        return res

    def get_queryset(self):
        return Operations_refsQuerySet(self.model, using=self._db)


class Operations_refs(Model):
    child = ForeignKeyProtect(Operations, related_name='child_Operation')
    parent = ForeignKeyProtect(Operations, related_name='parent_Operation', blank=True, null=True)


    objects = Operations_refsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'

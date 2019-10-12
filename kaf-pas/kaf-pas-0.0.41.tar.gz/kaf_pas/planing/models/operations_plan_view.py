import logging

from django.db.models import BooleanField

from isc_common.models.audit import AuditManager, AuditQuerySet
from kaf_pas.planing.models.operations_plan import OperationsPlan

logger = logging.getLogger(__name__)


class Operations_plan_viewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Operations_plan_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'isFolder': record.isFolder,
        }
        return res

    def get_queryset(self):
        return Operations_plan_viewQuerySet(self.model, using=self._db)


class Operations_plan_view(OperationsPlan):
    isFolder = BooleanField()

    objects = Operations_plan_viewManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'production_operationsplan_view'
        managed = False
        verbose_name = 'Операции планировая'

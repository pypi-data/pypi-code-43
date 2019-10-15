import logging

from django.db.models import DateTimeField, DecimalField
from django.utils import timezone

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.ckk.models.status import Status
from kaf_pas.planing.models.operation_plan_types import Operation_plan_types
from kaf_pas.planing.models.operations_plan_status import OperationsPlanStatus

logger = logging.getLogger(__name__)


class OperationsPlanQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class OperationsPlanManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'quantity': record.quantity,
            'description': record.description,
        }
        return res

    def get_queryset(self):
        return OperationsPlanQuerySet(self.model, using=self._db)


class OperationsPlan(AuditModel):
    status = ForeignKeyProtect(OperationsPlanStatus)

    opertype = ForeignKeyProtect(Operation_plan_types)

    objects = OperationsPlanManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Операции планировая'

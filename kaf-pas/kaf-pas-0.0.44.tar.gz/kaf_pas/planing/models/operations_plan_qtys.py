import logging

from django.db.models import DecimalField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.planing.models.operations_plan import OperationsPlan

logger = logging.getLogger(__name__)


class Operations_plan_sumsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Operations_plan_sumsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {}
        return res

    def get_queryset(self):
        return Operations_plan_sumsQuerySet(self.model, using=self._db)


class Operations_plan_qtys(AuditModel):
    quantity = DecimalField(max_digits=20, decimal_places=8)
    operations_plan = ForeignKeyProtect(OperationsPlan)
    objects = Operations_plan_sumsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Суммы'

import logging

from django.db.models import Model

from isc_common.fields.related import ForeignKeyProtect
from kaf_pas.planing.models.operations_plan import OperationsPlan

logger = logging.getLogger(__name__)


class Operations_plan_refs(Model):
    child = ForeignKeyProtect(OperationsPlan, related_name='child_Operations_plan')
    parent = ForeignKeyProtect(OperationsPlan, related_name='parent_Operations_plan', blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'

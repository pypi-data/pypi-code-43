import logging

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Item_operationsQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Item_operationsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
        }
        return res

    def get_queryset(self):
        return Item_operationsQuerySet(self.model, using=self._db)


class Item_operations(AuditModel):
    item = ForeignKeyCascade(Item)
    operation = ForeignKeyCascade(Operations)

    objects = Item_operationsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'

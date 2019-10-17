import logging

from django.db.models import PositiveIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.sales.models.precent import Precent

logger = logging.getLogger(__name__)


class Precent_itemsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Precent_itemsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            'item_id': record.item.id,
            'item__STMP_1': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'item__STMP_2': record.item.STMP_2.value_str if record.item.STMP_2 else None,
            'location_id': record.location.id if record.location else None,
            'location__code': record.location.code if record.location else None,
            'location__name': record.location.name if record.location else None,
            'precent_id': record.precent.id,
            'qty': record.qty,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return Precent_itemsQuerySet(self.model, using=self._db)


class Precent_items(AuditModel):
    item = ForeignKeyProtect(Item)
    precent = ForeignKeyProtect(Precent)
    location = ForeignKeyProtect(Locations, null=True, blank=True)
    qty = PositiveIntegerField()

    objects = Precent_itemsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Комплектация распоряжения'
        # unique_together = (('item', 'precent'),)

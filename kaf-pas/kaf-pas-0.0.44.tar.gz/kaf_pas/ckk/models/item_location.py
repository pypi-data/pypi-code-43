import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations

logger = logging.getLogger(__name__)


class Item_locationQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Item_locationManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {}
        return res

    def get_queryset(self):
        return Item_locationQuerySet(self.model, using=self._db)


class Item_location(AuditModel):
    item = ForeignKeyProtect(Item)
    location = ForeignKeyProtect(Locations)

    objects = Item_locationManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        unique_together = (('item', 'location'),)
        verbose_name = 'Размещение товарных позиций по местам'

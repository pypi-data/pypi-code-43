import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.ckk.models.item import Item

logger = logging.getLogger(__name__)


class Item_refsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def update(self, **kwargs):
        return super().update(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        return super().get_or_create(defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        return super().update_or_create(defaults, **kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Item_refsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Item_refsQuerySet(self.model, using=self._db)


class Item_refs(AuditModel):
    child = ForeignKeyProtect(Item, related_name='child')
    parent = ForeignKeyProtect(Item, related_name='parent', blank=True, null=True)

    def __str__(self):
        return f'\nID={self.id} child=[{self.child}], parent=[{self.parent}]'

    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.id == self.child.id:
                raise Exception(f'Attempt to record with parent.id ({self.parent.id}) == child.id ({self.child.id})')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Item_refs'
        unique_together = ('child', 'parent')

import logging

from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.item import Item

logger = logging.getLogger(__name__)


class Item_refs(AuditModel):
    child = ForeignKeyProtect(Item, related_name='child')
    parent = ForeignKeyProtect(Item, related_name='parent', blank=True, null=True)

    def __str__(self):
        return f'\nID={self.id} child=[{self.child}], parent=[{self.parent}]'

    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.id == self.child.id:
                raise Exception(f'parent.id ({self.parent.id}) == child.id ({self.child.id})')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Item_refs'
        unique_together = ('child', 'parent')

import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeySetNull
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_refs import Item_refs

logger = logging.getLogger(__name__)


class Item_refs(AuditModel):
    item_refs = ForeignKeySetNull(Item_refs, null=True, blank=True)
    child = ForeignKeyProtect(Item, related_name='child_production')
    parent = ForeignKeyProtect(Item, related_name='parent_production', blank=True, null=True)

    def __str__(self):
        return f'\nID={self.id} child=[{self.child}], parent=[{self.parent}]'

    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.id == self.child.id:
                logger.warning(f'Attempt to record with parent.id ({self.parent.id}) == child.id ({self.child.id})')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Строка производственной спецификации'
        unique_together = ('item_refs', 'child', 'parent')

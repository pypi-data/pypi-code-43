import logging

from django.db import transaction
from django.db.models import BigIntegerField, BooleanField, PositiveIntegerField
from django.forms import model_to_dict

from isc_common import delAttr, setAttr, getAttr
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from kaf_pas.ckk.models.item import Item_add, Item
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Item_operations_viewQuerySet(AuditQuerySet):

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Item_operations_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "STMP_1_id": record.STMP_1.id if record.STMP_1 else None,
            "STMP_1__value_str": record.STMP_1.value_str if record.STMP_1 else None,
            "STMP_2_id": record.STMP_2.id if record.STMP_2 else None,
            "STMP_2__value_str": record.STMP_2.value_str if record.STMP_2 else None,
            "lastmodified": record.lastmodified,
            "document_id": record.document.id if record.document else None,
            "document__file_document": record.document.file_document if record.document else None,
            "parent_id": record.parent_id,
            "editing": record.editing,
            "deliting": record.deliting,
            "isFolder": record.isFolder,
            "relevant": record.relevant,
            "version": record.version,
            "where_from": record.where_from,
            "qty_operations": record.qty_operations,
            "props": int(record.props),
        }
        # print(res)
        return res

    def get_queryset(self):
        return Item_operations_viewQuerySet(self.model, using=self._db)

class Item_operations_view(AuditModel):
    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_view_operations', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_view_operations', null=True, blank=True)
    document = ForeignKeyProtect(Documents, verbose_name='Документ', null=True, blank=True)
    parent_id = BigIntegerField()
    relevant = NameField()
    where_from = NameField()
    props = Item_add.get_prop_field()
    version = PositiveIntegerField(null=True, blank=True)
    qty_operations = PositiveIntegerField()

    isFolder = BooleanField()

    objects = Item_operations_viewManager()

    @property
    def item(self):
        from kaf_pas.ckk.models.item import Item
        return Item.objects.get(id=self.id)

    def __str__(self):
        return f"ID={self.id} STMP_1=[{self.STMP_1}], STMP_2=[{self.STMP_2}], props={self.props}"

    class Meta:
        managed = False
        db_table = 'ckk_item_operations_view'
        verbose_name = 'Товарная позиция'

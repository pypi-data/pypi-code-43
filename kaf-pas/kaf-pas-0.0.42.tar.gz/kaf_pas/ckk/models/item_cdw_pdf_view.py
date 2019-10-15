import logging

from bitfield import BitField
from django.db.models import BigIntegerField, BooleanField, PositiveIntegerField

from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from kaf_pas.ckk.models.item import Item_add
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Cdw_Pdf_Item_viewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Cdw_Pdf_Item_viewManager(AuditManager):

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
            "props": int(record.props),
        }
        # print(res)
        return res

    def get_queryset(self):
        return Cdw_Pdf_Item_viewQuerySet(self.model, using=self._db)


class Cdw_Pdf_Item_view(AuditModel):
    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_cdw', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_cdw', null=True, blank=True)
    isFolder = BooleanField(verbose_name='Обозначение изделия')
    document = ForeignKeyProtect(Documents, verbose_name='Документ', null=True, blank=True)
    parent_id = BigIntegerField(null=True, blank=True)
    relevant = NameField()
    props = Item_add.get_prop_field()

    objects = Cdw_Pdf_Item_viewManager()


    def __str__(self):
        return f"{self.STMP_1}: {self.STMP_2} (props : {self.props} ,type document: {self.document.attr_type.code}, deleted_at: {self.deleted_at})"
        # return f"id: {self.id}, parent_id: {self.parent.id}, relevant: {self.relevant},  isFolder: {self.isFolder}"


    class Meta:
        managed = False
        # db_table = 'ckk_cdw_pdf_item_view'
        db_table = 'ckk_item_view'
        verbose_name = 'Чертеж'

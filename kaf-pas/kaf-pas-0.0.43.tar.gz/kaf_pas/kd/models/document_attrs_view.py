import logging

from bitfield import BitField
from django.db.models import TextField, PositiveIntegerField, BigIntegerField

from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.document_attributes import Document_attributesQuerySet, Document_attributesManager
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Document_attrs_viewQuerySet(Document_attributesQuerySet):

    def get_attr(self, document, code):
        try:
            return Document_attrs_view.objects.get(document=document, attr_type__code=code)
        except Document_attrs_view.DoesNotExist:
            return None


class Document_attrs_viewManager(Document_attributesManager):
    def get_queryset(self):
        return Document_attrs_viewQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__description": record.attr_type.description if record.attr_type else None,
            "section": record.section,
            "subsection": record.subsection,
            "value_str": record.value_str,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res


class Document_attrs_view(AuditModel):
    document = ForeignKeyCascade(Documents, verbose_name='Документ')
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип атрибута')
    value_str = TextField(verbose_name="Значение атрибута", db_index=True)
    section = NameField()
    subsection = NameField()
    position_in_document = PositiveIntegerField()
    cross_id = BigIntegerField()

    objects = Document_attrs_viewManager()

    def __str__(self):
        return self.value_str

    class Meta:
        verbose_name = 'Аттрибуты докуменнта'
        managed = False
        db_table = 'kd_document_attrs_view'

import logging

from django.db.models import TextField, PositiveIntegerField

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.document_attributes import Document_attributesQuerySet
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Document_attributes_viewManager(CommonManagetWithLookUpFieldsManager):

    def get_queryset(self):
        return Document_attributesQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__description": record.attr_type.description if record.attr_type else None,
            "value_str": record.value_str,
            "value_int": record.value_int,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res


class Document_attributes_view(AuditModel):
    document = ForeignKeyCascade(Documents, verbose_name='Документ')
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип атрибута')
    value_str = TextField(verbose_name="Значение атрибута", db_index=True)
    value_int = PositiveIntegerField(verbose_name="Значение атрибута", db_index=True)
    section = CodeField(verbose_name="Раздел", null=True, blank=True)
    subsection = CodeField(verbose_name="Подраздел", null=True, blank=True)
    position_in_document = PositiveIntegerField()

    def __str__(self):
        return self.value_str

    class Meta:
        verbose_name = 'Аттрибуты докуменнта'
        managed = False
        db_table = 'kd_document_attrs_view'

import logging

from bitfield import BitField
from django.db.models import TextField

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Document_attrsQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def get_attr(self, document, code):
        res = super().filter(document=document, attr_type__code=code)
        _len = len(res)
        if _len == 1:
            return res[0]
        elif _len > 1:
            logger.warning(f'document: {document} has attr:{code} {_len}')
            return res[0]
        else:
            return None


class Document_attrsManager(CommonManagetWithLookUpFieldsManager):
    def get_queryset(self):
        return Document_attrsQuerySet(self.model, using=self._db)

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


class Document_attrs(AuditModel):
    # DEPRECATED !!!!!!!!!!!!!!!!!

    document = ForeignKeyCascade(Documents, verbose_name='Документ')
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип атрибута')

    section = CodeField(verbose_name="Раздел", null=True, blank=True)
    subsection = CodeField(verbose_name="Подраздел", null=True, blank=True)
    value_str = TextField(verbose_name="Значение атрибута", db_index=True)

    props = BitField(flags=(
        ('relevant', 'Актуальность'),
        ('copied', 'Копированный')
    ), default=1, db_index=True)

    objects = Document_attrsManager()

    def __str__(self):
        return self.value_str

    class Meta:
        verbose_name = 'Аттрибуты докуменнта'
        unique_together = (('document', 'attr_type', 'section', 'subsection'),)

import logging

from django.db.models import Model, PositiveIntegerField

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Document_attr_cross(Model):
    document = ForeignKeyCascade(Documents)
    attribute = ForeignKeyCascade(Document_attributes)
    position_in_document = PositiveIntegerField()

    section = CodeField(verbose_name="Раздел", null=True, blank=True)
    subsection = CodeField(verbose_name="Подраздел", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.attribute.attr_type.code == 'STMP_1' or self.attribute.attr_type.code == 'STMP_2':
            try:
                Document_attr_cross.objects.get(attribute=self.attribute, document=self.document)
                raise Exception(f'Попытка записи дубликата: {self.attribute}')
            except Document_attr_cross.DoesNotExist:
                ...
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('document', 'position_in_document'),)

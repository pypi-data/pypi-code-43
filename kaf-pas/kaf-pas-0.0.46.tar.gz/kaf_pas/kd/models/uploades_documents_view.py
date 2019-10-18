import logging

from django.db.models import BigAutoField, BigIntegerField, DateTimeField, BooleanField, Model
from django.utils import timezone

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditManager, AuditQuerySet
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.uploades import Uploades

logger = logging.getLogger(__name__)


class Uploades_documentsViewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Uploades_documentsViewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'document_id': record.document.id,
            'document__path_id': record.document.path.id,
            'STMP_1_id': record.STMP_1.id if record.STMP_1 else None,
            'STMP_1__value_str': record.STMP_1.value_str if record.STMP_1 else None,
            'STMP_2_id': record.STMP_2.id if record.STMP_2 else None,
            'STMP_2__value_str': record.STMP_2.value_str if record.STMP_2 else None,
            'document__attr_type_id': record.document.attr_type.id,
            'document__attr_type__code': record.document.attr_type.code,
            'document__attr_type__name': record.document.attr_type.name,
            'document__file_document': record.document.file_document,
            'document__file_size': record.document.file_size,
            'document__lastmodified': record.document.lastmodified,
            'document__file_modification_time': record.document.file_modification_time,
            'document__file_access_time': record.document.file_access_time,
            'document__file_change_time': record.document.file_change_time,
        }
        return res

    def get_queryset(self):
        return Uploades_documentsViewQuerySet(self.model, using=self._db)


class Uploades_documents_view(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    deleted_at = DateTimeField(verbose_name="Дата мягкого удаления", null=True, blank=True, db_index=True)
    editing = BooleanField(verbose_name="Возможность редактирования", default=True)
    deliting = BooleanField(verbose_name="Возможность удаления", default=True)
    lastmodified = DateTimeField(verbose_name='Последнее обновление', editable=False, db_index=True, default=timezone.now)

    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_upload_doc_view', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_upload_doc_view', null=True, blank=True)

    upload = ForeignKeyCascade(Uploades)
    document = ForeignKeyCascade(Documents)

    objects = Uploades_documentsViewManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'kd_uploades_documents_view'
        managed = False

import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_view import Documents_view
from kaf_pas.kd.models.uploades import Uploades

logger = logging.getLogger(__name__)


class Uploades_documentsQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Uploades_documentsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        document_view = record.document_view
        res = {
            'id': record.id,
            'document_id': record.document.id,
            'document__path_id': record.document.path.id,
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
        return Uploades_documentsQuerySet(self.model, using=self._db)


class Uploades_documents(AuditModel):
    upload = ForeignKeyCascade(Uploades)
    document = ForeignKeyCascade(Documents)

    objects = Uploades_documentsManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        unique_together = (('upload', 'document'),)

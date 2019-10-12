import logging

from django.db import transaction
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.kd.models.pathes import Pathes

logger = logging.getLogger(__name__)


class UploadesQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class UploadesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'lastmodified': record.lastmodified,
            'path_id': record.path.id,
            'absolute_path': record.path.absolute_path
        }
        return res

    def get_queryset(self):
        return UploadesQuerySet(self.model, using=self._db)

    def deleteFromRequest(self, request):
        from kaf_pas.kd.models.uploades_documents import Uploades_documents
        from kaf_pas.kd.models.documents_thumb import Documents_thumb
        from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10
        from kaf_pas.kd.models.document_attr_cross import Document_attr_cross
        from kaf_pas.ckk.models.item import Item
        from kaf_pas.ckk.models.item import ItemManager
        from kaf_pas.kd.models.documents_history import Documents_history
        from kaf_pas.kd.models.documents import Documents
        from kaf_pas.kd.models.uploades_log import Uploades_log

        ids = request.GET.getlist('ids')

        res = 0
        with transaction.atomic():
            for i in range(0, len(ids), 2):
                id = ids[i]
                visibleMode = ids[i + 1]

                if visibleMode != "none":
                    res += super().filter(id=id).soft_delete(visibleMode=visibleMode)
                else:
                    for upload_document in Uploades_documents.objects.filter(upload_id=id):

                        Document_attr_cross.objects.filter(document=upload_document.document).delete()

                        for item in Item.objects.filter(document=upload_document.document):
                            ItemManager.delete_recursive(item, True)

                        for documents_history in Documents_history.objects.filter(new_document=upload_document.document):
                            documents_history.old_document.props |= Documents.props.relevant
                            documents_history.old_document.save()
                            documents_history.delete()

                        Documents_thumb.objects.filter(document=upload_document.document).delete()
                        Documents_thumb10.objects.filter(document=upload_document.document).delete()
                        document = Documents.objects.get(id=upload_document.document.id)
                        logger.debug(f'Deliting: {document}')
                        document.delete()
                        logger.debug('Done.')
                    Uploades_log.objects.filter(upload_id=id).delete()
                    res += super().filter(id=id).delete()[0]
        return res


class Uploades(AuditModel):
    path = ForeignKeyCascade(Pathes)
    objects = UploadesManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Загрузки внешних данных'

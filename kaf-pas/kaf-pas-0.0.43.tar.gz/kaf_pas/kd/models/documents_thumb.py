import logging
import os

from django.db import transaction
from django.db.models import TextField

from crypto.models.crypto_file import CryptoManager, Crypto_file
from isc_common.fields.related import ForeignKeyProtect
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10

logger = logging.getLogger(__name__)


class Documents_thumbManager(CryptoManager):
    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "path": record.file_name,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
            "file_document_thumb_url": f'/logic/DocumentsThumb/Download/{record.id}/'
        }
        return res

    def deleteFromRequest(self, request, removed=None, ):
        res = 0
        ids = request.GET.getlist('ids')

        with transaction.atomic():
            for i in range(0, len(ids), 2):
                id = ids[i]
                mode = ids[i + 1]

                if mode == 'hide':
                    for item in super().filter(id=id):
                        item.soft_delete()
                        Documents_thumb10.objects.filter(path=item.path).soft_delete()
                        res += 1
                else:
                    for item in super().filter(id=id):
                        item.delete()
                        Documents_thumb10.objects.filter(path=item.path).delete()
                        res += 1
        return res


class Documents_thumb(Crypto_file):
    # Менять на cascade нельзя, потому как не происходит удаленеи файлов изображений при удалении документа
    document = ForeignKeyProtect(Documents, verbose_name='КД')
    path = TextField()

    @property
    def file_name(self):
        dir, filename = os.path.split(self.path)
        return filename

    objects = Documents_thumbManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'JPEG варианты документов уменьшенная копия'

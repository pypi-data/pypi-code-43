import logging

from django.db.models import TextField

from crypto.models.crypto_file import Crypto_file, CryptoManager
from isc_common.fields.related import ForeignKeyProtect
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class Documents_thumb10(Crypto_file):
    # Менять на cascade нельзя, потому как не происходит удаленеи файлов изображений при удалении документа
    document = ForeignKeyProtect(Documents, verbose_name='КД')
    path = TextField()

    objects = CryptoManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'JPEG варианты документов'

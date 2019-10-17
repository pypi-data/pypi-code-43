import logging

from bitfield import BitField
from django.db.models import DateTimeField

from crypto.models.crypto_file import Crypto_file

logger = logging.getLogger(__name__)


class Files_askon(Crypto_file):
    file_modification_time = DateTimeField(verbose_name='Дата время поcледнего модификации документа')
    props = BitField(flags=(('imp', 'Импорт'),), db_index=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Файлы АСКОНа'

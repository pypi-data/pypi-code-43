from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.kd.models.uploades import Uploades

logger = logging.getLogger(__name__)

class Uploades_logQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Uploades_logManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'upload_id': record.upload.id,
            'lastmodified': record.lastmodified,
            'log': record.log,
        }
        return res

    def get_queryset(self):
        return Uploades_logQuerySet(self.model, using=self._db)


class  Uploades_log(AuditModel):
    log = TextField()
    upload = ForeignKeyCascade(Uploades)

    objects = Uploades_logManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Строки лога закачки'

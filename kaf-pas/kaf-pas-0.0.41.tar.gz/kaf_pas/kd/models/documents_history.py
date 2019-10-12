from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)

class Documents_historyQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Documents_historyManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Documents_historyQuerySet(self.model, using=self._db)


class  Documents_history(AuditModel):
    old_document = ForeignKeyCascade(Documents,related_name='old_document')
    new_document = ForeignKeyCascade(Documents,related_name='new_document')

    objects = Documents_historyManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('old_document', 'new_document'),)

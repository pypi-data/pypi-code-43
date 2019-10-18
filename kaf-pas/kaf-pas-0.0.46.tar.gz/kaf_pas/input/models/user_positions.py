import logging

from isc_common.models.audit import AuditQuerySet, AuditManager
from isc_common.models.base_ref import BaseRef

logger = logging.getLogger(__name__)


class User_positionsQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class User_positionsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
        }
        return res

    def get_queryset(self):
        return User_positionsQuerySet(self.model, using=self._db)


class User_positions(BaseRef):
    objects = User_positionsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Должности'

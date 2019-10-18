import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager
from isc_common.models.base_ref import BaseRef, BaseRefHierarcy, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class locationsQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class LocationsManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return locationsQuerySet(self.model, using=self._db)


class Locations(BaseRefHierarcy):
    objects = LocationsManager()


def __str__(self):
    return f"{self.id}"


class Meta:
    verbose_name = 'Место положения'

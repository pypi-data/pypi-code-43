import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.ckk.models.locations import Locations

logger = logging.getLogger(__name__)


class ResourceQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class ResourceManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            # "location_id": record.location.id,
            # "location__code": record.location.code,
            # "location__name": record.location.name,
            # "location__full_name": record.location.full_name,
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return ResourceQuerySet(self.model, using=self._db)


class Resource(BaseRefHierarcy):
    location = ForeignKeyProtect(Locations)
    objects = ResourceManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Ресурсы'

import logging

from django.db.models import BooleanField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.ckk.models.locations import Locations

logger = logging.getLogger(__name__)


class Resource_viewQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Resource_viewManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'isFolder': record.isFolder,
            # "location_id": record.location.id,
            # "location__code": record.location.code,
            # "location__name": record.location.name,
            # "location__full_name": record.location.full_name,
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return Resource_viewQuerySet(self.model, using=self._db)

    @property
    def full_name(self):
        return f'{self.location.full_name}/{super().full_name}'


class Resource_view(BaseRefHierarcy):
    location = ForeignKeyProtect(Locations)
    isFolder = BooleanField()

    objects = Resource_viewManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'production_resource_view'
        managed = False
        verbose_name = 'Ресурсы'

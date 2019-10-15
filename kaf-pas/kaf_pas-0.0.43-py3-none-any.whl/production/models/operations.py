import logging

from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy

logger = logging.getLogger(__name__)


class OperationsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class OperationsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "code": record.code,
            "name": record.name,
            "full_name": record.full_name,
            "description": record.description,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
        }
        return res

    def get_queryset(self):
        return OperationsQuerySet(self.model, using=self._db)


class Operations(BaseRefHierarcy):
    objects = OperationsManager()

    def __str__(self):
        return f"ID={self.id}, code={self.code}, name={self.name}, description={self.description}"

    class Meta:
        verbose_name = 'Операции'

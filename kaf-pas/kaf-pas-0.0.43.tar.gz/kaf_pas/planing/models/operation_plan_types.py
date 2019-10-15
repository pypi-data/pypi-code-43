import logging

from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRef, BaseRefQuerySet, BaseRefManager

logger = logging.getLogger(__name__)


class Operation_plan_typesQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Operation_plan_typesManager(BaseRefManager):

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
        return Operation_plan_typesQuerySet(self.model, using=self._db)


class Operation_plan_types(BaseRef):
    objects = Operation_plan_typesManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Типи операций планирования'

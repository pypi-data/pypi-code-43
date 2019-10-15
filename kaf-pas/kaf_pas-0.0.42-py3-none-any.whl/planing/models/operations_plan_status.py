from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef

logger = logging.getLogger(__name__)


class OperationsPlanStatusQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class OperationsPlanStatusManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return OperationsPlanStatusQuerySet(self.model, using=self._db)


class OperationsPlanStatus(BaseRef):
    objects = OperationsPlanStatusManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Статусы операций'

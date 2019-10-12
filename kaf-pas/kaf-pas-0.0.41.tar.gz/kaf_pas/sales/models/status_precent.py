from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.models.base_ref import BaseRefManager, BaseRef, BaseRefQuerySet

logger = logging.getLogger(__name__)


class StatusPrecentQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class StatusPrecentManager(BaseRefManager):

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
        return StatusPrecentQuerySet(self.model, using=self._db)


class StatusPrecent(BaseRef):
    objects = StatusPrecentManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Статусы распоряжения'

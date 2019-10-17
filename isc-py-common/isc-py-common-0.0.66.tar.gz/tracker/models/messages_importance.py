from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Messages_importanceQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Messages_importanceManager(BaseRefManager):

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
        return Messages_importanceQuerySet(self.model, using=self._db)


class Messages_importance(BaseRef):
    objects = Messages_importanceManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Важность дел'

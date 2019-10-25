import logging

from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Prod_task_statusQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Prod_task_statusManager(BaseRefManager):

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
        return Prod_task_statusQuerySet(self.model, using=self._db)


class Prod_task_status(BaseRef):
    objects = Prod_task_statusManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Статусы заданий в производство'

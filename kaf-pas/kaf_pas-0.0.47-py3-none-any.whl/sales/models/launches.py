import logging

from django.db.models import DateTimeField, PositiveIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefManager, BaseRefQuerySet
from kaf_pas.sales.models.demand import Demand
from kaf_pas.sales.models.status_launch import Status_launch

logger = logging.getLogger(__name__)


class LaunchesQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class LaunchesManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,

            'demand_id': record.precent.id,
            'demand__code': record.precent.code,
            'demand__date': record.precent.date,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'qty': record.qty,
        }
        return res

    def get_queryset(self):
        return LaunchesQuerySet(self.model, using=self._db)


class Launches(BaseRefHierarcy):
    date = DateTimeField()
    status = ForeignKeyProtect(Status_launch)
    demand = ForeignKeyProtect(Demand)
    qty = PositiveIntegerField()
    objects = LaunchesManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Запуски'

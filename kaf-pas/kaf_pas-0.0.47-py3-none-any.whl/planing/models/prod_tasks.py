import logging

from django.db.models import PositiveIntegerField, DateTimeField
from django.forms import model_to_dict

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from kaf_pas.ckk.models.item import Item
from kaf_pas.planing.models.operations_plan_status import OperationsPlanStatus
from kaf_pas.planing.models.prod_task_importances import Prod_task_importances

logger = logging.getLogger(__name__)


class Prod_tasksQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Prod_tasksManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'create_date': record.create_date,
            'description': record.description,
            'importances_id': record.importances.id,
            'importances__name': record.importances.name,
            'status_id': record.status.id,
            'status__name': record.status.name,
            'creator_id': record.creator.id,
            'creator__short_name': record.creator.get_short_name,
        }
        return res

    def get_queryset(self):
        return Prod_tasksQuerySet(self.model, using=self._db)


    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        setAttr(_data, 'creator_id', request.user_id)

        res = super().create(**_data)
        res = model_to_dict(res)
        data.update(res)
        return data


class Prod_tasks(BaseRef):
    item = ForeignKeyProtect(Item)
    creator = ForeignKeyProtect(User)
    importances = ForeignKeyProtect(Prod_task_importances)
    status = ForeignKeyProtect(OperationsPlanStatus)
    qty_plain = PositiveIntegerField('Количество по плану')
    create_date = DateTimeField('Дата')

    objects = Prod_tasksManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Задания в производство'

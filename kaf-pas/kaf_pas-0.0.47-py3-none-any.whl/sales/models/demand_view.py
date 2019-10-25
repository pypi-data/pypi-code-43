import logging

from django.db.models import PositiveIntegerField, DateTimeField, BooleanField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.sales.models.precent import Precent
from kaf_pas.sales.models.precent_dogovors import Precent_dogovors
from kaf_pas.sales.models.precent_items import Precent_items
from kaf_pas.sales.models.status_demand import Status_demand

logger = logging.getLogger(__name__)


class Demand_viewQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Demand_viewManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'date': record.date,
            'date_sign': record.precent.date_sign,
            'qty': record.qty,
            'parent_id': record.parent.id if record.parent else None,

            'precent_id': record.precent.id,
            'precent__code': record.precent.code,
            'precent__date': record.precent.date,

            'precent_dogovor_id': record.precent_dogovor.id,
            'precent_dogovor__code': record.precent_dogovor.dogovor.code,
            'precent_dogovor__date': record.precent_dogovor.dogovor.date,

            'precent_item_id': record.precent_item.id,
            'precent_item__STMP_1_id': record.precent_item.item.STMP_1.id if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_1__value_str': record.precent_item.item.STMP_1.value_str if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_2_id': record.precent_item.item.STMP_2.id if record.precent_item.item.STMP_2 else None,
            'precent_item__STMP_2__value_str': record.precent_item.item.STMP_2.value_str if record.precent_item.item.STMP_2 else None,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'isFolder': record.isFolder,
        }
        return res

    def get_queryset(self):
        return Demand_viewQuerySet(self.model, using=self._db)


class Demand_view(BaseRefHierarcy):
    date = DateTimeField()
    precent = ForeignKeyProtect(Precent)
    precent_dogovor = ForeignKeyProtect(Precent_dogovors)
    precent_item = ForeignKeyProtect(Precent_items)
    status = ForeignKeyProtect(Status_demand)
    qty = PositiveIntegerField()
    isFolder = BooleanField()

    objects = Demand_viewManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Заказы на продажу'
        db_table = 'sales_demand_view'
        managed = False

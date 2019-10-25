import logging

from django.db import transaction
from django.db.models import PositiveIntegerField, DateTimeField

from isc_common import delAttr, setAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.sales.models.precent import Precent
from kaf_pas.sales.models.precent_dogovors import Precent_dogovors
from kaf_pas.sales.models.precent_items import Precent_items
from kaf_pas.sales.models.precent_items_view import Precent_items_view
from kaf_pas.sales.models.status_demand import Status_demand

logger = logging.getLogger(__name__)


class DemandQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class DemandManager(CommonManagetWithLookUpFieldsManager):

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
        }
        return res

    def get_queryset(self):
        return DemandQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        from kaf_pas.sales.models.demand_materials import Demand_materials

        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        precent = _data.get('precent')
        if precent:
            with transaction.atomic():
                precent_id = precent.get('precent_id')
                setAttr(_data, 'precent_id', precent_id)
                precent_dogovor_id = precent.get('precent_dogovor_id')
                setAttr(_data, 'precent_dogovor_id', precent_dogovor_id)
                precent_item_id = precent.get('precent_item_id')
                setAttr(_data, 'precent_item_id', precent_item_id)
                delAttr(_data, 'precent')
                _qty = _data.get('qty')

                for precent_item in Precent_items.objects.filter(id=precent_item_id).select_for_update():
                    qty = Precent_items_view.objects.get(id=precent_item.id).qty
                    if _qty > qty:
                        raise Exception(f'Нет затребованного количества. В наличии {qty}, затребовано: {_qty}')
                    res = super().create(**_data)
                    setAttr(_data, 'id', res.id)

                    precent_material_ids = precent.get('precent_material_ids')
                    if isinstance(precent_material_ids, list):
                        for precent_material_id in precent_material_ids:
                            Demand_materials.objects.get_or_create(demand=res, precent_material_id=precent_material_id)

        return _data

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()

        _data = data.copy()
        with transaction.atomic():
            for precent_item in Precent_items.objects.filter(id=data.get('precent_item_id')).select_for_update():
                qty = Precent_items_view.objects.get(id=precent_item.id).qty
                if data.get('qty') > qty:
                    raise Exception(f'Нет затребованного количества. В наличии {qty}, затребовано: {data.get("qty")}')
            delAttr(_data, 'date_sign')
            super().filter(id=data.get('id')).update(**_data)

        return data


class Demand(BaseRefHierarcy):
    date = DateTimeField()
    precent = ForeignKeyProtect(Precent)
    precent_dogovor = ForeignKeyProtect(Precent_dogovors)
    precent_item = ForeignKeyProtect(Precent_items)
    status = ForeignKeyProtect(Status_demand)
    qty = PositiveIntegerField()

    objects = DemandManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Заказы на продажу'

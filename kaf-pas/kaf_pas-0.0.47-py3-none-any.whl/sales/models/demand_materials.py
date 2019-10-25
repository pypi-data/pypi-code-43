import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.sales.models.demand import Demand
from kaf_pas.sales.models.precent_materials import Precent_materials

logger = logging.getLogger(__name__)


class Demand_materialsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def create(self, **kwargs):
        return self._create_or_update(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Demand_materialsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            'material_askon_id': record.precent_material.material_askon.id if record.precent_material.material_askon else None,
            'material_askon__field0': record.precent_material.material_askon.field0 if record.precent_material.material_askon else None,

            'material_id': record.precent_material.material.id if record.precent_material.material else None,
            'material__name': record.precent_material.material.name if record.precent_material.material else None,

            'complex_name': record.precent_material.complex_name,
            'complex_gost': record.precent_material.complex_gost,

            'edizm_id': record.precent_material.edizm.id,
            'edizm__code': record.precent_material.edizm.code,
            'edizm__name': record.precent_material.edizm.name,

            'qty': record.precent_material.qty,

            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return Demand_materialsQuerySet(self.model, using=self._db)


class Demand_materials(AuditModel):
    demand = ForeignKeyCascade(Demand)
    precent_material = ForeignKeyProtect(Precent_materials)

    @property
    def complex_name(self):
        if self.precent_material.material:
            return f'{self.precent_material.material.materials_type.full_name}{self.precent_material.material.full_name}'
        else:
            return None

    @property
    def complex_gost(self):
        if self.precent_material.material:
            if self.precent_material.material.materials_type.gost:
                return f'{self.precent_material.material.materials_type.gost} / {self.precent_material.material.gost}'
            else:
                return f'{self.precent_material.material.gost}'
        else:
            return None

    objects = Demand_materialsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'

import logging

from django.db.models import PositiveIntegerField

from isc_common import setAttr, delAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.material_askon import Material_askon
from kaf_pas.ckk.models.materials import Materials
from kaf_pas.sales.models.precent_items import Precent_items

logger = logging.getLogger(__name__)


class Precent_materialsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def create(self, **kwargs):
        if kwargs.get('material'):
            setAttr(kwargs, 'material_id', kwargs.get('material').id)
            delAttr(kwargs, 'material')

        if kwargs.get('material_askon'):
            setAttr(kwargs, 'material_askon_id', kwargs.get('material_askon').id)
            delAttr(kwargs, 'material_askon')

        if not kwargs.get('material_id') and not kwargs.get('material_askon_id'):
            raise Exception('Необходим хотябы один выпбранный параметр.')
        return self._create_or_update(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Precent_materialsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            'material_askon_id': record.material_askon.id if record.material_askon else None,
            'material_askon__field0': record.material_askon.field0 if record.material_askon else None,

            'material_id': record.material.id if record.material else None,
            'material__name': record.material.name if record.material else None,

            'complex_name': record.complex_name,
            'complex_gost': record.complex_gost,

            'edizm_id': record.edizm.id,
            'edizm__code': record.edizm.code,
            'edizm__name': record.edizm.name,

            'qty': record.qty,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return Precent_materialsQuerySet(self.model, using=self._db)


class Precent_materials(AuditModel):
    precent_item = ForeignKeyProtect(Precent_items)
    material = ForeignKeyProtect(Materials, null=True, blank=True)
    material_askon = ForeignKeyProtect(Material_askon, null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm, default=None)
    qty = PositiveIntegerField()

    @property
    def complex_name(self):
        if self.material:
            return f'{self.material.materials_type.full_name}{self.material.full_name}'
        else:
            return None

    @property
    def complex_gost(self):
        if self.material:
            if self.material.materials_type.gost:
                return f'{self.material.materials_type.gost} / {self.material.gost}'
            else:
                return self.material.gost
        else:
            return None

    objects = Precent_materialsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Комплектация'

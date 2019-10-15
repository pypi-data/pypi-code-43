import logging

from django.db.models import PositiveIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.materials import Materials
from kaf_pas.sales.models.precent import Precent

logger = logging.getLogger(__name__)


class Precent_materialsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Precent_materialsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            'material_id': record.material.id,
            'material__code': record.material.code,
            'material__name': record.material.name,
            'qty': record.qty,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return Precent_materialsQuerySet(self.model, using=self._db)


class Precent_materials(AuditModel):
    precent = ForeignKeyProtect(Precent)
    material = ForeignKeyProtect(Materials)
    objects = Precent_materialsManager()
    qty = PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'

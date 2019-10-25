import logging

from django.db.models import DecimalField

from isc_common.fields.code_field import CodeStrictField
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy

logger = logging.getLogger(__name__)


class Ed_izmQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Ed_izmManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'koef_recalc': record.koef_recalc,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return Ed_izmQuerySet(self.model, using=self._db)


class Ed_izm(BaseRefHierarcy):
    code = CodeStrictField(unique=True)
    koef_recalc = DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    objects = Ed_izmManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Единицы измерения'

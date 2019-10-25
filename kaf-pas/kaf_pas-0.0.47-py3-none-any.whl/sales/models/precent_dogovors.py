import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.sales.models.dogovors import Dogovors
from kaf_pas.sales.models.precent import Precent

logger = logging.getLogger(__name__)


class Precent_dogovorsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Precent_dogovorsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'dogovor_id': record.dogovor.id,
            'dogovor__code': record.dogovor.code,
            'dogovor__date': record.dogovor.date,
        }
        return res

    def get_queryset(self):
        return Precent_dogovorsQuerySet(self.model, using=self._db)


class Precent_dogovors(AuditModel):
    dogovor = ForeignKeyProtect(Dogovors)
    precent = ForeignKeyProtect(Precent)

    objects = Precent_dogovorsManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Кросс-таблица'

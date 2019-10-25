import logging

from django.db.models import CharField

from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy

logger = logging.getLogger(__name__)


class Material_typeQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Material_typeManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'gost': record.gost,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res

    def get_queryset(self):
        return Material_typeQuerySet(self.model, using=self._db)


class Material_type(BaseRefHierarcy):
    code = CharField(max_length=255, unique=True)
    gost = CodeField()
    name = CharField(max_length=255)
    objects = Material_typeManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Тип материала'

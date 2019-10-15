import logging

from django.db.models import CharField, BooleanField

from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy

logger = logging.getLogger(__name__)


class Material_type_viewQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Material_type_viewManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'isFolder': record.isFolder,
            'gost': record.gost,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res

    def get_queryset(self):
        return Material_type_viewQuerySet(self.model, using=self._db)


class Material_type_view(BaseRefHierarcy):
    code = CharField(max_length=255, unique=True)
    gost = CodeField()
    name = CharField(max_length=255)
    objects = Material_type_viewManager()
    isFolder = BooleanField()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'ckk_material_type_view'
        managed = False
        verbose_name = 'Тип материала'

import logging

from django.db.models import CharField, BooleanField

from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.base_ref import Hierarcy

logger = logging.getLogger(__name__)


class Material_askon_mviewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Material_askon_mviewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'field0': record.field0,
            'field1': record.field1,
            'field2': record.field2,
            'field3': record.field3,
            'field4': record.field4,
            'field5': record.field5,
            'field6': record.field6,
            'field7': record.field7,
            'isFolder': record.isFolder,
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return Material_askon_mviewQuerySet(self.model, using=self._db)


class Material_askon_mview(Hierarcy):
    field0 = CharField(verbose_name='Информация в дерево материалов', db_index=True, max_length=255)
    field1 = CharField(verbose_name='Материал.Наименование и документ', null=True, blank=True, max_length=255)
    field2 = CharField(verbose_name='Материал.Код', null=True, blank=True, max_length=255)
    field3 = CharField(verbose_name='Сортамент.Наименование и документ', null=True, blank=True, max_length=255)
    field4 = CharField(verbose_name='Экземпляр сортамента.Типоразмер', null=True, blank=True, max_length=255)
    field5 = CharField(verbose_name='Экземпляр сортамента.Обозначение', null=True, blank=True, max_length=255)
    field6 = CharField(verbose_name='Экземпляр сортамента.Статус', null=True, blank=True, max_length=255)
    field7 = CharField(verbose_name='Экземпляр сортамента.Код', null=True, blank=True, max_length=255)
    isFolder = BooleanField()

    objects = Material_askon_mviewManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Материалы из Асона'
        managed = False
        db_table = 'ckk_material_askon_mview'

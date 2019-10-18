import logging

from django.db.models import CharField

from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.base_ref import Hierarcy

logger = logging.getLogger(__name__)


class Material_askonQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Material_askonManager(AuditManager):

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
            'parent_id': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return Material_askonQuerySet(self.model, using=self._db)


class Material_askon(Hierarcy):
    field0 = CharField(verbose_name='Информация в дерево материалов', db_index=True, max_length=255)
    field1 = CharField(verbose_name='Материал.Наименование и документ', null=True, blank=True, max_length=255)
    field2 = CharField(verbose_name='Материал.Код', null=True, blank=True, max_length=255)
    field3 = CharField(verbose_name='Сортамент.Наименование и документ', null=True, blank=True, max_length=255)
    field4 = CharField(verbose_name='Экземпляр сортамента.Типоразмер', null=True, blank=True, max_length=255)
    field5 = CharField(verbose_name='Экземпляр сортамента.Обозначение', null=True, blank=True, max_length=255)
    field6 = CharField(verbose_name='Экземпляр сортамента.Статус', null=True, blank=True, max_length=255)
    field7 = CharField(verbose_name='Экземпляр сортамента.Код', null=True, blank=True, max_length=255)
    objects = Material_askonManager()

    def __str__(self):
        return f"field0: {self.field0} field1: {self.field1} field2: {self.field2} field3: {self.field3} field4: {self.field4} field5: {self.field5} field6: {self.field6} field7: {self.field7}"

    class Meta:
        verbose_name = 'Материалы из Асона'
        unique_together = (('field0', 'field1', 'field2', 'field3', 'field4', 'field5', 'field6', 'field7'),)

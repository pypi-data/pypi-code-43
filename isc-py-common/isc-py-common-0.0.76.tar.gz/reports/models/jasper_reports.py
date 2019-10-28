import logging

from isc_common.models.base_ref import BaseRefHierarcy, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Jasper_reportsQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Jasper_reportsManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None
        }
        return res

    def get_queryset(self):
        return Jasper_reportsQuerySet(self.model, using=self._db)


class Jasper_reports(BaseRefHierarcy):
    objects = Jasper_reportsManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Отчеты'

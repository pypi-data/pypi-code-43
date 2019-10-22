import logging

from django.db.models import PositiveIntegerField, TextField, BooleanField

from isc_common.fields.code_field import CodeStrictField
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Type_paramQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Type_paramManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'type': record.type,
            'length': record.length,
            # 'precision': record.precision,
            # 'exponent': record.exponent,
        }
        return res

    def get_queryset(self):
        return Type_paramQuerySet(self.model, using=self._db)


class Type_param(BaseRef):
    @staticmethod
    def string():
        return 'Строковый'

    @staticmethod
    def date():
        return 'Дата без времени'

    @staticmethod
    def date_time():
        return 'Дата со временем'

    @staticmethod
    def integer():
        return 'Целое число'

    @staticmethod
    def float():
        return 'Дробное число'

    @staticmethod
    def select():
        return 'Выбор из списка'

    type = CodeStrictField(default='Строка')
    value_map = TextField(null=True, blank=True)
    length = PositiveIntegerField(default=255, null=True, blank=True)
    required = BooleanField(default=False)

    objects = Type_paramManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Тип параметр'

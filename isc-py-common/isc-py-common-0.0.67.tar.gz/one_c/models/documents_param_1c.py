import logging

from django.db.models import TextField, Model, UUIDField, BooleanField, FloatField, IntegerField

from isc_common.fields.related import ForeignKeyProtect
from one_c.models.param_type import Param_type

logger = logging.getLogger(__name__)


class Documents_param_1c(Model):
    type = ForeignKeyProtect(Param_type)
    value = TextField(db_index=True, null=True, blank=True)
    value_boolean = BooleanField(db_index=True, null=True, blank=True)
    value_float = FloatField(db_index=True, null=True, blank=True)
    value_int = IntegerField(db_index=True, null=True, blank=True)
    value_uuid = UUIDField(db_index=True, null=True, blank=True)

    def __str__(self):
        return f"(id: {self.id}, " \
            f"document: type: {self.type}, " \
            f"value: {self.value}, " \
            f"value_uuid: {self.value_uuid}, " \
            f"value_boolean: {self.value_boolean}, " \
            f"value_float: {self.value_float}, " \
            f"value_int: {self.value_int})"

    class Meta:
        verbose_name = 'Параметры документов 1С'
        unique_together = (('type', 'value', 'value_boolean', 'value_float', 'value_int', 'value_uuid'),)

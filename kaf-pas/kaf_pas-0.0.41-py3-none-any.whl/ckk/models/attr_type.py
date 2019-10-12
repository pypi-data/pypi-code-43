import logging

from bitfield import BitField

from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager
from isc_common.models.base_ref import BaseRef

logger = logging.getLogger(__name__)


class AttrManager(AuditManager):
    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "code": record.code,
            "name": record.name,
            "description": record.description,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_attr(self, code, name=None, default=None):
        try:
            if name:
                return super().get_queryset().get(code=code, name=name)
            else:
                return super().get_queryset().get(code=code)
        except Attr_type.DoesNotExist as e:
            if default:
                return default
            else:
                raise e


class Attr_type(BaseRef):

    code = CodeField(verbose_name="Код", db_index=True, unique=True)
    name = NameField(verbose_name="Наименование", db_index=True)
    props = BitField(flags=(('relevant', 'Актуальность'),), default=1, db_index=True)
    parent = ForeignKeyProtect("self", null=True, blank=True)

    relevent_label = "Действует"
    not_relevent_label = "Не действует"

    objects = AttrManager()

    def __str__(self):
        return f"ID={self.id}, code={self.code} name={self.name} props={self.props}"

    class Meta:
        verbose_name = 'Тип атрибута'

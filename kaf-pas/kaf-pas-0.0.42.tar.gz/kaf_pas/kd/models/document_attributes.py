import logging

from django.db import transaction
from django.db.models import TextField, BigIntegerField

from isc_common import setAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type

logger = logging.getLogger(__name__)


class Document_attributesQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def create(self, **kwargs):
        value_str = kwargs.get('value_str')
        value_int = Document_attributesManager.to_int(value_str)

        if not kwargs.get('attr_type_id'):
            attr_type = Attr_type.objects.get(code=kwargs.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)
        setAttr(kwargs, 'value_int', value_int)

        return super().create(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        value_str = kwargs.get('value_str')

        if not kwargs.get('attr_type_id') and kwargs.get('attr_type__code'):
            attr_type = Attr_type.objects.get(code=kwargs.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)
        elif isinstance(defaults, dict) and not defaults.get('attr_type_id') and defaults.get('attr_type__code'):
            attr_type = Attr_type.objects.get(code=defaults.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)

        if not value_str and isinstance(defaults, dict):
            value_str = defaults.get('value_str')
            value_int = Document_attributesManager.to_int(value_str)
            setAttr(defaults, 'value_int', value_int)
        else:
            value_int = Document_attributesManager.to_int(value_str)
            setAttr(kwargs, 'value_int', value_int)

        return super().get_or_create(defaults, **kwargs)

    def update(self, **kwargs):
        value_str = kwargs.get('value_str')
        value_int = Document_attributesManager.to_int(value_str)
        if not kwargs.get('attr_type_id'):
            attr_type = Attr_type.objects.get(code=kwargs.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)
        setAttr(kwargs, 'value_int', value_int)

        return super().update(**kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        value_str = kwargs.get('value_str')

        if not kwargs.get('attr_type_id') and kwargs.get('attr_type__code'):
            attr_type = Attr_type.objects.get(code=kwargs.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)
        elif isinstance(defaults, dict) and not defaults.get('attr_type_id') and defaults.get('attr_type__code'):
            attr_type = Attr_type.objects.get(code=defaults.get('attr_type__code'))
            setAttr(kwargs, 'attr_type_id', attr_type.id)

        if not value_str and isinstance(defaults, dict):
            value_str = defaults.get('value_str')
            value_int = Document_attributesManager.to_int(value_str)
            setAttr(defaults, 'value_int', value_int)
        else:
            value_int = Document_attributesManager.to_int(value_str)
            setAttr(kwargs, 'value_int', value_int)

        return super().get_or_create(defaults, **kwargs)


class Document_attributesManager(CommonManagetWithLookUpFieldsManager):
    def get_queryset(self):
        return Document_attributesQuerySet(self.model, using=self._db)

    @staticmethod
    def to_int(str):
        try:
            res = int(str)
            if res > 9223372036854775807:
                return None
            else:
                return res

        except:
            return None

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__description": record.attr_type.description if record.attr_type else None,
            "value_str": record.value_str,
            "value_int": record.value_int,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def update_document_attributes(self, document_attribute):
        with transaction.atomic():
            Document_attributes.objects.filter(id=document_attribute.get('id')).update(**document_attribute)
            return document_attribute

    def updateFromRequest(self, request, removed=None, function=None):
        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()
        return self.update_document_attributes(data)


class Document_attributes(AuditModel):
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип атрибута')
    value_str = TextField(verbose_name="Значение атрибута", db_index=True, null=True, blank=True)
    value_int = BigIntegerField(verbose_name="Значение атрибута", db_index=True, null=True, blank=True)

    objects = Document_attributesManager()

    def __str__(self):
        return f'ID={self.id}, attr_type=[{self.attr_type}], attr_type__code=[{self.attr_type.code}], value_str={self.value_str}'

    class Meta:
        verbose_name = 'Аттрибуты докуменнта'
        unique_together = (('attr_type', 'value_str'),)

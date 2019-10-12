import logging

from django.db import transaction
from django.db.models import TextField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type

logger = logging.getLogger(__name__)


class Document_attributesQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Document_attributesManager(CommonManagetWithLookUpFieldsManager):
    def get_queryset(self):
        return Document_attributesQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__description": record.attr_type.description if record.attr_type else None,
            "value_str": record.value_str,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def update_document_attributes(self, document_attribute):
        with transaction.atomic():
            # for document_attribute_old in super().filter(
            #         attr_type_id=document_attribute.get('attr_type_id'),
            #         value_str=document_attribute.get('value_str')).select_for_update():
            #
            #     for item in Item.objects.filter(STMP_1=document_attribute_old).select_for_update():
            #         item.STMP_1_id = document_attribute.get('id')
            #         item.save()
            #
            #     for item in Item.objects.filter(STMP_2=document_attribute_old).select_for_update():
            #         item.STMP_2 = document_attribute.get('id')
            #         item.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_FORMAT=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_FORMAT = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_ZONE=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_ZONE = document_attribute_old
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_POS=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_POS = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_MARK=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_MARK = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_NAME=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_NAME = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_COUNT=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_COUNT = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_NOTE=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_NOTE = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_MASSA=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_MASSA = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_MATERIAL=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_MATERIAL = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_USER=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_USER = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_KOD=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_KOD = document_attribute.get('id')
            #         item_line.save()
            #
            #     for item_line in Item_line.objects.filter(SPC_CLM_FACTORY=document_attribute_old).select_for_update():
            #         item_line.SPC_CLM_FACTORY = document_attribute.get('id')
            #         item_line.save()
            #     document_attribute_old.delete()

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

    objects = Document_attributesManager()

    def save(self, *args, **kwargs):
        if self.value_str == None:
            try:
                Document_attributes.objects.get(value_str__isnull=True, attr_type=self.attr_type)
                raise Exception(f'Элемент с пустым значением уже существует.')
            except Document_attributes.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID={self.id}, attr_type=[{self.attr_type}], attr_type__code=[{self.attr_type.code}], value_str={self.value_str}'

    class Meta:
        verbose_name = 'Аттрибуты докуменнта'
        unique_together = (('attr_type', 'value_str'),)

import logging

from django.db.models import PositiveIntegerField

from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.ckk.models.item import Item_add
from kaf_pas.ckk.models.item_line import Item_lineManager
from kaf_pas.kd.models.document_attributes import Document_attributes

logger = logging.getLogger(__name__)


class Item_line_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'child_id': record.child.id if record.child else None,
            'parent_id': record.parent.id,
            'SPC_CLM_FORMAT_id': record.SPC_CLM_FORMAT.id if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_FORMAT__value_str': record.SPC_CLM_FORMAT.value_str if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_ZONE_id': record.SPC_CLM_ZONE.id if record.SPC_CLM_ZONE else None,
            'SPC_CLM_ZONE__value_str': record.SPC_CLM_ZONE.value_str if record.SPC_CLM_ZONE else None,
            'SPC_CLM_POS_id': record.SPC_CLM_POS.id if record.SPC_CLM_POS else None,
            'SPC_CLM_POS__value_str': record.SPC_CLM_POS.value_str if record.SPC_CLM_POS else None,
            'SPC_CLM_POS__value_int': record.SPC_CLM_POS.value_int if record.SPC_CLM_POS else None,
            'SPC_CLM_MARK_id': record.SPC_CLM_MARK.id if record.SPC_CLM_MARK else None,
            'SPC_CLM_MARK__value_str': record.SPC_CLM_MARK.value_str if record.SPC_CLM_MARK else None,
            'SPC_CLM_NAME_id': record.SPC_CLM_NAME.id if record.SPC_CLM_NAME else None,
            'SPC_CLM_NAME__value_str': record.SPC_CLM_NAME.value_str if record.SPC_CLM_NAME else None,
            'SPC_CLM_COUNT_id': record.SPC_CLM_COUNT.id if record.SPC_CLM_COUNT else None,
            'SPC_CLM_COUNT__value_str': record.SPC_CLM_COUNT.value_str if record.SPC_CLM_COUNT else None,
            'SPC_CLM_NOTE_id': record.SPC_CLM_NOTE.id if record.SPC_CLM_NOTE else None,
            'SPC_CLM_NOTE__value_str': record.SPC_CLM_NOTE.value_str if record.SPC_CLM_NOTE else None,
            'SPC_CLM_MASSA_id': record.SPC_CLM_MASSA.id if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MASSA__value_str': record.SPC_CLM_MASSA.value_str if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MATERIAL_id': record.SPC_CLM_MATERIAL.id if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_MATERIAL__value_str': record.SPC_CLM_MATERIAL.value_str if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_USER_id': record.SPC_CLM_USER.id if record.SPC_CLM_USER else None,
            'SPC_CLM_USER__value_str': record.SPC_CLM_USER.value_str if record.SPC_CLM_USER else None,
            'SPC_CLM_KOD_id': record.SPC_CLM_KOD.id if record.SPC_CLM_KOD else None,
            'SPC_CLM_KOD__value_str': record.SPC_CLM_KOD.value_str if record.SPC_CLM_KOD else None,
            'SPC_CLM_FACTORY_id': record.SPC_CLM_FACTORY.id if record.SPC_CLM_FACTORY else None,
            'SPC_CLM_FACTORY__value_str': record.SPC_CLM_FACTORY.value_str if record.SPC_CLM_FACTORY else None,
            'section': record.section,
            'section_num': record.section_num,
            'subsection': record.subsection,
            'where_from': record.where_from,
            'lastmodified': record.lastmodified,
            'editing': record.editing,
            'deliting': record.deliting,
            'item_props': record.item_props._value,
            'relevant': record.relevant,
            'icon': Item_lineManager.getIcon(record.section)
        }
        return res


class Item_line_view(AuditModel):
    parent = ForeignKeyProtect('Item', verbose_name='Товарная позиция', related_name='item_parent_v')
    child = ForeignKeyCascade('Item', verbose_name='Товарная позиция', related_name='item_child_v')

    SPC_CLM_FORMAT = ForeignKeyProtect(Document_attributes, verbose_name='Формат', related_name='SPC_CLM_FORMAT_v', null=True, blank=True)
    SPC_CLM_ZONE = ForeignKeyProtect(Document_attributes, verbose_name='Зона', related_name='SPC_CLM_ZONE_v', null=True, blank=True)
    SPC_CLM_POS = ForeignKeyProtect(Document_attributes, verbose_name='Позиция', related_name='SPC_CLM_POS_v', null=True, blank=True)
    SPC_CLM_MARK = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение', related_name='SPC_CLM_MARK_v', null=True, blank=True)
    SPC_CLM_NAME = ForeignKeyProtect(Document_attributes, verbose_name='Наименование', related_name='SPC_CLM_NAME_v', null=True, blank=True)
    SPC_CLM_COUNT = ForeignKeyProtect(Document_attributes, verbose_name='Количество', related_name='SPC_CLM_COUNT_v', null=True, blank=True)
    SPC_CLM_NOTE = ForeignKeyProtect(Document_attributes, verbose_name='Примечание', related_name='SPC_CLM_NOTE_v', null=True, blank=True)
    SPC_CLM_MASSA = ForeignKeyProtect(Document_attributes, verbose_name='Масса', related_name='SPC_CLM_MASSA_v', null=True, blank=True)
    SPC_CLM_MATERIAL = ForeignKeyProtect(Document_attributes, verbose_name='Материал', related_name='SPC_CLM_MATERIAL_v', null=True, blank=True)
    SPC_CLM_USER = ForeignKeyProtect(Document_attributes, verbose_name='Пользовательская', related_name='SPC_CLM_USER_v', null=True, blank=True)
    SPC_CLM_KOD = ForeignKeyProtect(Document_attributes, verbose_name='Код', related_name='SPC_CLM_KOD_v', null=True, blank=True)
    SPC_CLM_FACTORY = ForeignKeyProtect(Document_attributes, verbose_name='Предприятие - изготовитель', related_name='SPC_CLM_FACTORY_v', null=True, blank=True)
    section = NameField()
    section_num = PositiveIntegerField(default=0)
    subsection = NameField()

    where_from = NameField()
    item_props = Item_add.get_prop_field()
    relevant = NameField()

    objects = Item_line_viewManager()

    class Meta:
        verbose_name = 'Строка состава изделия'
        db_table = 'ckk_item_line_view'
        managed = False
        # proxy = True

import logging

from bitfield import BitField, BitHandler
from django.db import transaction
from django.db.models import PositiveIntegerField
from django.forms import model_to_dict

from isc_common import getAttr, setAttr, delAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents

logger = logging.getLogger(__name__)


class ItemQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class ItemManager(CommonManagetWithLookUpFieldsManager):

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        parent = _data.get('parent')
        if parent:
            delAttr(_data, 'parent')
            setAttr(_data, 'parent_id', parent)

        delAttr(_data, 'STMP_1__value_str')
        delAttr(_data, 'STMP_2__value_str')

        relevant = data.get('relevant')
        props = 1

        if relevant:
            if relevant == 'Актуален':
                props |= Item.props.relevant
            else:
                props &= ~Item.props.relevant

        where_from = data.get('where_from')
        if where_from == 'Получено из чертежа':
            props |= Item.props.from_cdw
        elif where_from == 'Получено из спецификации':
            props |= Item.props.from_spw
        elif where_from == 'Получено из бумажного архива':
            props |= Item.props.from_pdf
        elif where_from == 'Занесено вручную':
            props |= Item.props.man_input

        delAttr(_data, 'relevant')
        delAttr(_data, 'where_from')
        setAttr(_data, 'props', props)

        res = super().create(**_data)
        logger.debug(f'Added: {res}')

        from kaf_pas.ckk.models.item_refs import Item_refs
        item_refs, create = Item_refs.objects.get_or_create(parent_id=_data.get('parent_id'), child=res)
        if create:
            logger.debug(f'Added item_ref: {item_refs}')

        res = model_to_dict(res)

        props = getAttr(res, 'props')
        if props and isinstance(props, BitHandler):
            props = getAttr(res, 'props')._value
            setAttr(res, 'props', props)
        setAttr(res, 'isFolder', False)
        data.update(res)
        return data

    @staticmethod
    def delete_recursive(item, delete_lenes=False):
        with transaction.atomic():
            from kaf_pas.ckk.models.item_image_refs import Item_image_refs
            from kaf_pas.ckk.models.item_line import Item_line
            # from kaf_pas.ckk.models.item_location import Item_location
            from kaf_pas.ckk.models.item_refs import Item_refs

            Item_image_refs.objects.filter(item=item).delete()

            if delete_lenes:
                Item_line.objects.filter(parent=item).delete()
                Item_line.objects.filter(child=item).delete()

            Item_refs.objects.filter(parent=item).delete()
            Item_refs.objects.filter(child=item).delete()

            # Item_location.objects.filter(item=item).delete()
            item.delete()

    def updateFromRequest(self, request, removed=None, function=None):
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.ckk.models.item_line import Item_line

        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()

        with transaction.atomic():
            targetRecord = data.get('targetRecord')
            dropRecords = data.get('dropRecords')
            if data.get('mode') == 'move':
                res = 0
                for dropRecord in dropRecords:
                    res += Item_refs.objects.filter(parent_id=dropRecord.get('parent_id'), child_id=dropRecord.get('id')).update(parent_id=targetRecord.get('id'))
                    res += Item_line.objects.filter(parent_id=dropRecord.get('parent_id'), child_id=dropRecord.get('id')).update(parent_id=targetRecord.get('id'))
                return res
            elif data.get('mode') == 'copy':
                res = 0
                for dropRecord in dropRecords:
                    Item_refs.objects.create(parent_id=targetRecord.get('id'), child_id=dropRecord.get('id'))
                    res += 1
                return res
            elif data.get('mode') == 'replace':
                res = 0
                for dropRecord in dropRecords:
                    Item_refs.objects.create(parent_id=targetRecord.get('parent_id'), child_id=dropRecord.get('id'))
                    res += 1

                    item_line = model_to_dict(Item_line.objects.get(parent_id=targetRecord.get('parent_id'), child_id=targetRecord.get('id')))
                    delAttr(item_line, 'id')
                    delAttr(item_line, 'parent')
                    delAttr(item_line, 'child')
                    setAttr(item_line, 'parent_id', targetRecord.get('parent_id'))
                    setAttr(item_line, 'child_id', dropRecord.get('id'))
                    setAttr(item_line, 'SPC_CLM_NAME_id', dropRecord.get('STMP_1_id'))
                    delAttr(item_line, 'SPC_CLM_NAME')
                    setAttr(item_line, 'SPC_CLM_MARK_id', dropRecord.get('STMP_2_id'))
                    delAttr(item_line, 'SPC_CLM_MARK')
                    setAttr(item_line, 'SPC_CLM_FORMAT_id', getAttr(item_line, 'SPC_CLM_FORMAT'))
                    delAttr(item_line, 'SPC_CLM_FORMAT')
                    setAttr(item_line, 'SPC_CLM_ZONE_id', getAttr(item_line, 'SPC_CLM_ZONE'))
                    delAttr(item_line, 'SPC_CLM_ZONE')
                    setAttr(item_line, 'SPC_CLM_POS_id', getAttr(item_line, 'SPC_CLM_POS'))
                    delAttr(item_line, 'SPC_CLM_POS')
                    setAttr(item_line, 'SPC_CLM_COUNT_id', getAttr(item_line, 'SPC_CLM_COUNT'))
                    delAttr(item_line, 'SPC_CLM_COUNT')
                    setAttr(item_line, 'SPC_CLM_NOTE_id', getAttr(item_line, 'SPC_CLM_NOTE'))
                    delAttr(item_line, 'SPC_CLM_NOTE')
                    setAttr(item_line, 'SPC_CLM_MASSA_id', getAttr(item_line, 'SPC_CLM_MASSA'))
                    delAttr(item_line, 'SPC_CLM_MASSA')
                    setAttr(item_line, 'SPC_CLM_MATERIAL_id', getAttr(item_line, 'SPC_CLM_MATERIAL'))
                    delAttr(item_line, 'SPC_CLM_MATERIAL')
                    setAttr(item_line, 'SPC_CLM_USER_id', getAttr(item_line, 'SPC_CLM_USER'))
                    delAttr(item_line, 'SPC_CLM_USER')
                    setAttr(item_line, 'SPC_CLM_KOD_id', getAttr(item_line, 'SPC_CLM_KOD'))
                    delAttr(item_line, 'SPC_CLM_KOD')
                    setAttr(item_line, 'SPC_CLM_FACTORY_id', getAttr(item_line, 'SPC_CLM_FACTORY'))
                    delAttr(item_line, 'SPC_CLM_FACTORY')
                    Item_line.objects.create(**item_line)
                    res += 1

                    Item_refs.objects.filter(parent_id=targetRecord.get('parent_id'), child_id=targetRecord.get('id')).delete()
                    Item_line.objects.filter(parent_id=targetRecord.get('parent_id'), child_id=targetRecord.get('id')).delete()

                    try:
                        Item.objects.filter(id=targetRecord.get('id')).delete()
                    except Exception as ex:
                        logger.debug(ex)

                return res

            else:
                relevant = data.get('relevant')
                props = data.get('props')

                if relevant == 'Актуален':
                    props |= Item.props.relevant
                else:
                    props &= ~Item.props.relevant

                where_from = data.get('where_from')
                if where_from == 'Получено из чертежа':
                    props |= Item.props.from_cdw
                elif where_from == 'Получено из спецификации':
                    props |= Item.props.from_spw
                elif where_from == 'Получено из бумажного архива':
                    props |= Item.props.from_pdf
                elif where_from == 'Занесено вручную':
                    props |= Item.props.man_input

                delAttr(data, 'relevant')
                delAttr(data, 'where_from')
                setAttr(data, 'props', props)
                res = self.filter(id=data.get('id')).update(**data)

            return res

    def deleteFromRequest(self, request, removed=None, ):
        from kaf_pas.ckk.models.item_line import Item_line

        request = DSRequest(request=request)
        data = request.get_data()
        res = 0
        if data.get('mode') == 'deleteInner':
            record = data.get('record')

            from kaf_pas.ckk.models.item_refs import Item_refs
            res, _ = Item_refs.objects.filter(child_id=record.get('id'), parent_id=record.get('parent_id')).delete()
            return res

        with transaction.atomic():
            for id, mode in request.get_tuple_ids():
                if mode == 'hide':
                    res += super().filter(id=id).soft_delete()
                else:
                    from kaf_pas.ckk.models.item_refs import Item_refs
                    for item_refs in Item_refs.objects.filter(child_id=id):
                        res, _ = Item_refs.objects.filter(child_id=id, parent_id=item_refs.parent.id).delete()
                        res, _ = Item_refs.objects.filter(parent_id=id).delete()
                        res1, _ = Item_line.objects.filter(parent_id=id).delete()

                        res += res1
                    res = super().filter(id=id).delete()[0]

        return res

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'STMP_1_id': record.STMP_1.id if record.STMP_1 else None,
            'STMP_1__value_str': record.STMP_1.value_str if record.STMP_1 else None,
            'STMP_2_id': record.STMP_2.id if record.STMP_2 else None,
            'STMP_2__value_str': record.STMP_2.value_str if record.STMP_2 else None,
            'lastmodified': record.lastmodified,
            'version': record.version,
            'document_id': record.document.id if record.document else None,
            'document__file_document': record.document.file_document if record.document else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db)


class Item_add:
    @staticmethod
    def get_prop_field():
        return BitField(flags=(
            ('relevant', 'Актуальность'),  # 1
            ('from_cdw', 'Получено из чертежа'),  # 2
            ('from_spw', 'Получено из спецификации'),  # 4
            ('for_line', 'Строка спецификации'),  # 8
            ('from_pdf', 'Получено из бумажного архива'),  # 16
            ('man_input', 'Занесено вручную'),  # 32
            ('copied', 'Скопировано'),  # 64
        ), default=1, db_index=True)


class Item(AuditModel):
    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2', null=True, blank=True)
    version = PositiveIntegerField(null=True, blank=True)

    props = Item_add.get_prop_field()

    document = ForeignKeyProtect(Documents, verbose_name='Документ', null=True, blank=True)

    objects = ItemManager()

    @staticmethod
    def get_vaslue_str(doc_attr):
        if doc_attr.value_str == None:
            return None
        return doc_attr.value_str.strip() if doc_attr else None

    def save(self, *args, **kwargs):
        if ~self.props.relevant:
            item = Item.objects.filter()
            from django.db.models import Max

            res = item.aggregate(Max('version'))
            self.version = 1 if not res.get('version__max') else res.get('version__max') + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID={self.id} STMP_1=[{self.STMP_1}], STMP_2=[{self.STMP_2}], props={self.props}, version={self.version}'

    class Meta:
        verbose_name = 'Товарная позиция'
        unique_together = ('STMP_1', 'STMP_2', 'props', 'version')

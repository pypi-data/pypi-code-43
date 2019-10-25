import logging
import os
from os.path import getsize

from bitfield import BitField
from django.db import transaction
from django.db.models import DateTimeField, TextField, PositiveIntegerField

from isc_common import delAttr, replace_alt_set, setAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.management.commands.refresh_mat_views import refresh_mat_view
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.kd.models.pathes import Pathes

logger = logging.getLogger(__name__)


class DocumentQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class DocumentManager(CommonManagetWithLookUpFieldsManager):

    type_bad = Attr_type.objects.get_attr(code='KD_BAD')

    def get_queryset(self):
        return DocumentQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "path_id": record.path.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "file_document": record.file_document,
            "file_size": record.file_size,
            "file_modification_time": record.file_modification_time,
            "file_access_time": record.file_access_time,
            "file_change_time": record.file_change_time,
            "lastmodified": record.lastmodified,
            'load_error': f'<pre>{record.relevant}</pre>' if record.relevant else None,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_ex(self, *args, **kwargs):
        file_name = kwargs.get('file_document')
        file_drive = kwargs.get('file_drive')
        virt_path = kwargs.get('virt_path')
        attr_type = kwargs.get('attr_type')
        delAttr(kwargs, 'file_document')

        if virt_path:
            if virt_path[0:1] == os.sep or virt_path[0:1] == os.altsep:
                virt_path = virt_path[1:]

        if virt_path:
            if file_name.find(virt_path) == -1:
                _file_name = f'{virt_path}{os.sep}{file_name}'.replace(os.altsep, os.sep)
            else:
                _file_name = file_name.replace(os.altsep, os.sep)
        else:
            _file_name = file_name.replace(os.altsep, os.sep)

        for doc in Documents.objects.filter(path=kwargs.get('path'), attr_type=attr_type, props=Documents.props.relevant).exclude(attr_type=self.type_bad):
            real_file = replace_alt_set(f'{file_drive}{os.sep}{file_name}')

            if replace_alt_set(doc.file_document) == replace_alt_set(_file_name):
                real_file_size = getsize(real_file.replace(replace_alt_set(virt_path), '') if virt_path else real_file)

                # real_file_modification_time = datetime.fromtimestamp(getmtime(real_file)).replace(microsecond=0)
                # system_file_modification_time = doc.file_modification_time.replace(microsecond=0)

                # real_file_access_time = datetime.fromtimestamp(getatime(real_file)).replace(microsecond=0)
                # system_file_access_time = doc.file_access_time.replace(microsecond=0)
                #
                # real_file_change_time = datetime.fromtimestamp(getctime(real_file)).replace(microsecond=0)
                # system_file_change_time = doc.file_change_time.replace(microsecond=0)

                if doc.file_size != real_file_size:
                    # logger.debug(f'Неравенство размеров {doc.file_size} != {real_file_size}')
                    return doc, True
                # elif system_file_modification_time != real_file_modification_time:
                #     logger.debug(f'Неравенство file_modification_time {system_file_modification_time} != {real_file_modification_time}')
                #     return doc, True
                # elif system_file_access_time != real_file_access_time:
                #     logger.debug(f'Неравенство file_access_time {system_file_access_time} != {real_file_access_time}')
                #     return doc, True
                # elif system_file_change_time != real_file_change_time:
                #     logger.debug(f'Неравенство file_change_time {system_file_change_time} != {real_file_change_time}')
                #     return doc, True
                else:
                    return doc, False
        return None, None

    def updateFromRequest(self, request, removed=None, function=None):
        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()

        relevant = data.get('relevant')
        props = data.get('props')

        if relevant == 'Актуален':
            props |= Documents.props.relevant
        else:
            props &= ~Documents.props.relevant

        res = super().get(id=data.get('id'))
        res.props = props
        res.save()
        refresh_mat_view('kd_documents_mview')

        return data

    @staticmethod
    def delete(id):
        res = 0
        from kaf_pas.kd.models.document_attr_cross import Document_attr_cross
        from kaf_pas.kd.models.uploades_documents import Uploades_documents
        from kaf_pas.kd.models.documents_thumb import Documents_thumb
        from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10
        from kaf_pas.ckk.models.item import Item

        Uploades_documents.objects.filter(document_id=id).delete()
        Documents_thumb.objects.filter(document_id=id).delete()
        Documents_thumb.objects.filter(document_id=id).delete()
        Documents_thumb10.objects.filter(document_id=id).delete()
        Document_attr_cross.objects.filter(document_id=id).delete()
        for item in Item.objects.filter(document_id=id):
            from kaf_pas.ckk.models.item import ItemManager
            ItemManager.delete_recursive(item)
        res += Documents.objects.filter(id=id).delete()[0]
        return res

    def deleteFromRequest(self, request):
        from kaf_pas.ckk.models.item import Item
        from kaf_pas.ckk.models.item_image_refs import Item_image_refs
        from kaf_pas.kd.models.documents_thumb import Documents_thumb
        from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10

        ids = request.GET.getlist('ids')

        res = 0
        with transaction.atomic():
            for i in range(0, len(ids), 2):
                id = ids[i]
                visibleMode = ids[i + 1]

                if visibleMode != "none":
                    for item in Item.objects.filter(document_id=id):
                        # Item_refs.objects.filter(child=item).soft_delete(visibleMode=visibleMode)
                        # Item_refs.objects.filter(parent=item).soft_delete(visibleMode=visibleMode)

                        # Item_line.objects.filter(child=item).soft_delete(visibleMode=visibleMode)
                        # Item_line.objects.filter(parent=item).soft_delete(visibleMode=visibleMode)

                        Item_image_refs.objects.filter(item=item).soft_delete(visibleMode=visibleMode)

                        Documents_thumb.objects.filter(document_id=id).soft_delete(visibleMode=visibleMode)
                        Documents_thumb10.objects.filter(document_id=id).soft_delete(visibleMode=visibleMode)

                    Item.objects.filter(document_id=id).soft_delete(visibleMode=visibleMode)
                    res += super().filter(id=id).soft_delete(visibleMode=visibleMode)
                else:
                    res += DocumentManager.delete(id)
        refresh_mat_view('kd_documents_mview')
        return res

    @staticmethod
    def rec_image_cwd(item_id, STMP_2, logger):
        from kaf_pas.ckk.models.item_image_refs import Item_image_refs
        from kaf_pas.ckk.models.item import Item
        for item_image in Item_image_refs.objects.select_related('item').filter(item__props__in=[Item.props.relevant | Item.props.from_cdw, Item.props.relevant | Item.props.from_pdf], item__STMP_2__value_str=STMP_2):
            _, created = Item_image_refs.objects.get_or_create(item_id=item_id, thumb_id=item_image.thumb_id, thumb10_id=item_image.thumb10_id)
            if created:
                if logger:
                    logger.logging(f'\nAdded: {item_image}', 'debug')

    @staticmethod
    def del_blancks1(STMP_2):
        STMP_2_1 = ' '.join(STMP_2.split())
        if STMP_2_1 != STMP_2:
            return STMP_2_1
        return STMP_2

    @staticmethod
    def link_image_to_item(item, logger):
        from kaf_pas.ckk.models.item_image_refs import Item_image_refs
        from kaf_pas.kd.models.documents_thumb import Documents_thumb

        document = item.document

        for document_thumb in Documents_thumb.objects.filter(document=document):
            item_image_refs, created = Item_image_refs.objects.get_or_create(item=item, thumb=document_thumb)
            if logger:
                logger.logging(f'\nItem_image_refs: {item_image_refs}, created: {created}', 'debug')

        from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10
        for document_thumb10 in Documents_thumb10.objects.filter(document=document):
            item_image_refs, created = Item_image_refs.objects.get_or_create(item=item, thumb10=document_thumb10)
            if logger:
                logger.logging(f'\nItem_image_refs: {item_image_refs}, created: {created}', 'debug')

    @staticmethod
    def make_spw(document, top_auto_level_item, logger=None):
        from kaf_pas.kd.models.spw_attrs import Spw_attrs
        from kaf_pas.ckk.models.item import Item
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.kd.models.document_attributes import Document_attributes
        from kaf_pas.kd.models.spw_attrs import Spw_attrsQuerySet
        from kaf_pas.kd.models.document_attr_cross import Document_attr_cross

        with transaction.atomic():
            if document.file_document.lower().find('мусор') == -1:

                STMP_1 = Spw_attrs.objects.all().get_attr(document=document, code='STMP_1')
                STMP_2 = Spw_attrs.objects.all().get_attr(document=document, code='STMP_2')

                if STMP_1 != None or STMP_2 != None:
                    kwargs = dict(
                        STMP_1_id=STMP_1.id if STMP_1 else None,
                        STMP_2_id=STMP_2.id if STMP_2 else None,
                        props=Item.props.relevant | Item.props.from_spw
                    )

                    parent, created = Item.objects.get_or_create(
                        **kwargs,
                        defaults=dict(document=document))

                    if created:
                        item_refs = Item_refs.objects.create(parent=top_auto_level_item, child=parent)
                        if logger:
                            logger.logging(f'\nAdded: {item_refs} as tpo level', 'debug')

                    if kwargs.get('STMP_2__value_str') != None:
                        DocumentManager.rec_image_cwd(parent.id, kwargs.get('STMP_2__value_str'), logger)
                    DocumentManager.link_image_to_item(parent, logger)

                    query_spw = Spw_attrs.objects.filter(document=document).order_by(*['position_in_document'])
                    specification = Spw_attrsQuerySet.make_specification(queryResult=query_spw)

                    SPC_CLM_MARK_old = None
                    for line_specification in specification:
                        SPC_CLM_NAME = line_specification.get('SPC_CLM_NAME')
                        SPC_CLM_NAME_ID = line_specification.get('SPC_CLM_NAME_ID')

                        SPC_CLM_MARK = line_specification.get('SPC_CLM_MARK')
                        SPC_CLM_MARK_ID = line_specification.get('SPC_CLM_MARK_ID')

                        if SPC_CLM_NAME_ID != None or SPC_CLM_MARK_ID != None:

                            if isinstance(SPC_CLM_MARK, str) and SPC_CLM_MARK.startswith('-') and isinstance(SPC_CLM_MARK_ID, int):
                                SPC_CLM_MARK = f'{SPC_CLM_MARK_old}{SPC_CLM_MARK}'
                                for document_attribute in Document_attributes.objects.filter(id=SPC_CLM_MARK_ID):
                                    try:
                                        _document_attribute = Document_attributes.objects.get(attr_type=document_attribute.attr_type, value_str=SPC_CLM_MARK)
                                        Document_attr_cross.objects.filter(attribute=document_attribute).update(attribute=_document_attribute)
                                        setAttr(line_specification, 'SPC_CLM_MARK_ID', _document_attribute.id)
                                        # try:
                                        #     document_attribute.delete()
                                        # except Exception as ex:
                                        #     self.logging(ex, 'warning')
                                    except Document_attributes.DoesNotExist:
                                        document_attribute.value_str = SPC_CLM_MARK
                                        document_attribute.save()
                                        if logger:
                                            logger.logging(f'=================================================>>>>>> Uppdated: {SPC_CLM_MARK}')

                            elif isinstance(SPC_CLM_MARK, str):
                                SPC_CLM_MARK_old = SPC_CLM_MARK

                            child_args = dict(
                                STMP_1=SPC_CLM_NAME_ID,
                                STMP_2=SPC_CLM_MARK_ID,
                            )

                            _props = Item.props.relevant | Item.props.from_spw | Item.props.for_line

                            childs = list(Item.objects.filter(
                                STMP_1_id=child_args.get('STMP_1'),
                                STMP_2_id=child_args.get('STMP_2'),
                                props=_props,
                            ).order_by(*['version']))

                            if len(childs) > 1:
                                child, created = childs[0], False
                            else:
                                child, created = Item.objects.get_or_create(
                                    STMP_1_id=child_args.get('STMP_1'),
                                    STMP_2_id=child_args.get('STMP_2'),
                                    props=_props,
                                    defaults=dict(document=document)
                                )

                            if created:
                                if child.STMP_2 != None:
                                    DocumentManager.rec_image_cwd(child.id, child.STMP_2.value_str, logger)
                                if logger:
                                    logger.logging(f'\nAdded: {child} as child', 'debug')
                            else:
                                if logger:
                                    logger.logging(f'\nNot Added: {child} as child', 'debug')

                            item_refs, created = Item_refs.objects.get_or_create(parent=parent, child=child)
                            if created:
                                if logger:
                                    logger.logging(f'\nAdded: {item_refs}', 'debug')
                            else:
                                if logger:
                                    logger.logging(f'\nNot Added: {item_refs}', 'debug')

                            defaults = dict(
                                parent=parent,
                                child=child,
                                SPC_CLM_FORMAT_id=line_specification.get('SPC_CLM_FORMAT_ID'),
                                SPC_CLM_ZONE_id=line_specification.get('SPC_CLM_ZONE_ID'),
                                SPC_CLM_POS_id=line_specification.get('SPC_CLM_POS_ID'),
                                SPC_CLM_MARK_id=line_specification.get('SPC_CLM_MARK_ID'),
                                SPC_CLM_NAME_id=line_specification.get('SPC_CLM_NAME_ID'),
                                SPC_CLM_COUNT_id=line_specification.get('SPC_CLM_COUNT_ID'),
                                SPC_CLM_NOTE_id=line_specification.get('SPC_CLM_NOTE_ID'),
                                SPC_CLM_MASSA_id=line_specification.get('SPC_CLM_MASSA_ID'),
                                SPC_CLM_MATERIAL_id=line_specification.get('SPC_CLM_MATERIAL_ID'),
                                SPC_CLM_USER_id=line_specification.get('SPC_CLM_USER_ID'),
                                SPC_CLM_KOD_id=line_specification.get('SPC_CLM_KOD_ID'),
                                SPC_CLM_FACTORY_id=line_specification.get('SPC_CLM_FACTORY_ID'),

                                section=line_specification.get('section'),
                                subsection=line_specification.get('subsection'),
                            )

                            from kaf_pas.ckk.models.item_line import Item_line
                            item_line, created = Item_line.objects.get_or_create(parent=parent, child=child, defaults=defaults)
                            if created:
                                if logger:
                                    logger.logging(f'\nAdded: {item_line} as item_line', 'debug')
                            else:
                                if logger:
                                    logger.logging(f'\nNot Added: {item_line} as item_line', 'debug')

                else:
                    if logger:
                        logger.logging(f'\nSTMP_1 and STMP_2 is None, document: {document}', 'debug')
                    document.delete_soft()

            document.props |= Documents.props.beenItemed
            document.save()

    @staticmethod
    def make_cdw(document, logger=None):
        from kaf_pas.ckk.models.item_refs import Item_refs
        with transaction.atomic():
            if document.file_document.lower().find('мусор') == -1:
                from kaf_pas.kd.models.cdw_attrs import Cdw_attrs
                STMP_1 = Cdw_attrs.objects.all().get_attr(document=document, code='STMP_1')
                STMP_2 = Cdw_attrs.objects.all().get_attr(document=document, code='STMP_2')

                if STMP_1 != None or STMP_2 != None:

                    from kaf_pas.ckk.models.item import Item
                    args = dict(
                        STMP_1_id=STMP_1.id if STMP_1 else None,
                        STMP_2_id=STMP_2.id if STMP_2 else None,
                        props=Item.props.relevant | Item.props.from_cdw
                    )

                    cnt = 0
                    items = []

                    for item in Item.objects.filter(**args):

                        dir, file_name = os.path.split(document.file_document)
                        dir1, file_name1 = os.path.split(item.document.file_document)
                        if file_name == file_name1 and document.file_size == item.document.file_size:
                            items.append(item)
                            cnt += 1

                    if cnt == 0:
                        item, created = Item.objects.get_or_create(**args, defaults=dict(document=document))

                        if created:
                            if logger:
                                logger.logging(f'\nAdded: {item}, cdw', 'debug')
                        else:
                            if logger:
                                logger.logging('==============================================================================================================', 'debug')

                        try:
                            Item_refs.objects.get_or_create(child=item)
                        except Item_refs.MultipleObjectsReturned:
                            ...

                        DocumentManager.link_image_to_item(item, logger)
                    else:
                        for item in items:
                            if logger:
                                logger.logging(f'\nНайдено: элемент пришедший из {cnt + 1}-x источников : {item}', 'debug')
                            DocumentManager.link_image_to_item(item, logger)

                else:
                    if logger:
                        logger.logging(f'\nSTMP_1 is None and STMP_2 is None, document: {document}', 'debug')
                    document.delete_soft()

                document.props |= Documents.props.beenItemed
                document.save()

    @staticmethod
    def make_pdf(document, STMP_1_type, STMP_2_type, logger=None):
        from kaf_pas.kd.models.document_attributes import Document_attributes
        from kaf_pas.ckk.models.item_refs import Item_refs

        with transaction.atomic():
            if document.file_document.lower().find('мусор') == -1:
                full_path = document.file_document
                _, file_name = os.path.split(full_path)
                file_name_part = file_name.split(' - ')
                if len(file_name_part) == 2:

                    STMP_1, ext = os.path.splitext(file_name_part[1].strip())
                    STMP_2 = DocumentManager.del_blancks1(file_name_part[0].strip())
                else:
                    STMP_1 = str(file_name.strip()).replace('.pdf', '').replace('.PDF', '')
                    STMP_2 = STMP_1

                args = dict(
                    STMP_1=STMP_1,
                    STMP_2=STMP_2,
                )

                cnt = 0
                items = []
                from kaf_pas.ckk.models.item import Item
                for item in Item.objects.filter(
                        STMP_1__value_str=args.get('STMP_1'),
                        STMP_2__value_str=args.get('STMP_2'),
                        props=Item.props.relevant | Item.props.from_pdf
                ):

                    dir, file_name = os.path.split(document.file_document)
                    dir1, file_name1 = os.path.split(item.document.file_document)
                    if file_name == file_name1:
                        items.append(item)
                        cnt += 1

                if cnt == 0:
                    STMP_1_attr, _ = Document_attributes.objects.get_or_create(value_str=STMP_1, attr_type=STMP_1_type)
                    STMP_2_attr, _ = Document_attributes.objects.get_or_create(value_str=STMP_2, attr_type=STMP_2_type)

                    item, created = Item.objects.get_or_create(
                        STMP_1=STMP_1_attr,
                        STMP_2=STMP_2_attr,
                        document=document,
                        props=Item.props.relevant | Item.props.from_pdf,
                        defaults=dict(document=document)
                    )

                    if created:
                        if logger:
                            logger.logging(f'\nAdded: {item}', 'debug')
                    else:
                        if logger:
                            logger.logging('==============================================================================================================', 'debug')

                    try:
                        Item_refs.objects.get_or_create(child=item)
                    except Item_refs.MultipleObjectsReturned:
                        ...

                    DocumentManager.link_image_to_item(item, logger)
                else:
                    for item in items:
                        if logger:
                            logger.logging(f'\nНайдено: элемент пришедший из {cnt + 1}-x источников : {item}', 'debug')
                        DocumentManager.link_image_to_item(item, logger)

            document.props |= Documents.props.beenItemed
            document.save()


class Documents(AuditModel):
    path = ForeignKeyProtect(Pathes, verbose_name='Путь к документу')
    attr_type = ForeignKeyProtect(Attr_type, verbose_name='Тип документа')
    file_document = TextField(verbose_name='Полный путь к файлу', db_index=True)
    file_size = PositiveIntegerField(verbose_name='Размер файла')
    file_modification_time = DateTimeField(verbose_name='Дата время поcледнего модификации документа', null=True, blank=True, db_index=True)
    file_access_time = DateTimeField(verbose_name='Дата время поcледнего доступа к документу', null=True, blank=True, db_index=True)
    file_change_time = DateTimeField(verbose_name='Дата время изменнения документа', null=True, blank=True, db_index=True)
    props = BitField(flags=(
        ('relevant', 'Актуальность'),
        ('beenItemed', 'Был внесен в состав изделий'),
    ), default=1, db_index=True)
    load_error = TextField(null=True, blank=True)

    @property
    def file_name(self):
        (_, filename) = os.path.split(self.file_document)
        return filename

    objects = DocumentManager()

    @property
    def is_cdw(self):
        return self.attr_type.code == 'CDW'

    @property
    def is_spw(self):
        return self.attr_type.code == 'CPW'

    @property
    def is_pdf(self):
        dir, file = os.path.split(self.file_document)
        _, ext = os.path.splitext(file)
        if ext.lower() == '.pdf':
            return True
        else:
            return False

    def __str__(self):
        return f"ID: {self.id} {self.file_document} TYPE: {self.attr_type.code}"

    class Meta:
        verbose_name = 'Конструкторские документы'

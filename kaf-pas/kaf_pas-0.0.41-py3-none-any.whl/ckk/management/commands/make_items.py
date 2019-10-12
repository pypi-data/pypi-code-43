import logging
import os

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from isc_common import setAttr
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_image_refs import Item_image_refs
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.kd.models.cdw_attrs import Cdw_attrs
from kaf_pas.kd.models.cdws import Cdws
from kaf_pas.kd.models.document_attr_cross import Document_attr_cross
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_thumb import Documents_thumb
from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10
from kaf_pas.kd.models.pdfs import Pdfs
from kaf_pas.kd.models.spw_attrs import Spw_attrs, Spw_attrsQuerySet
from kaf_pas.kd.models.spws import Spws

logger = logging.getLogger(__name__)
logger1 = logging.getLogger(f'{__name__}_1')


class MakeItem:
    def meke_cdw(self, command_style=True):
        if command_style:
            self.pbar = tqdm(total=Cdws.objects.filter(props=~Documents.props.beenItemed).count())

        # <editor-fold desc="Этап 1">
        with transaction.atomic():
            for document in Cdws.objects.filter(props=~Documents.props.beenItemed):
                if document.file_document.lower().find('мусор') == -1:
                    # logger.debug(f'Iteming: {document}')

                    STMP_1 = Cdw_attrs.objects.all().get_attr(document=document, code='STMP_1')
                    STMP_2 = Cdw_attrs.objects.all().get_attr(document=document, code='STMP_2')

                    if STMP_1 != None or STMP_2 != None:

                        args = dict(
                            STMP_1_id=STMP_1.id if STMP_1 else None,
                            STMP_2_id=STMP_2.id if STMP_2 else None,
                            props=Item.props.relevant
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
                            item, created = Item.objects.get_or_create(**args, defaults=dict(document=document, props=Item.props.relevant | Item.props.from_cdw))

                            if created:
                                logger.debug(f'\nAdded: {item}, cdw')
                            else:
                                logger.debug('==============================================================================================================')

                            try:
                                Item_refs.objects.get_or_create(child=item)
                            except Item_refs.MultipleObjectsReturned:
                                ...

                            self.link_image_to_item(item)

                            # item.delete_soft()
                        else:
                            for item in items:
                                logger.debug(f'\nНайдено: элемент пришедший из {cnt + 1}-x источников : {item}')
                                self.link_image_to_item(item)

                    else:
                        logger.debug(f'\nSTMP_1 is None and STMP_2 is None, document: {document}')
                        document.delete_soft()

                document.props |= Documents.props.beenItemed
                document.save()

                if command_style and self.pbar:
                    self.pbar.update(1)

        if command_style and self.pbar:
            self.pbar.close()


class Command(BaseCommand):
    help = "Загрузка составов изделий"
    makeItem = MakeItem()

    def link_image_to_item(self, item):
        for document_thumb in Documents_thumb.objects.filter(document=item.document):
            item_image_refs, created = Item_image_refs.objects.get_or_create(item=item, thumb=document_thumb)
            logger.debug(f'\nItem_image_refs: {item_image_refs}, created: {created}')

        for document_thumb10 in Documents_thumb10.objects.filter(document=item.document):
            item_image_refs, created = Item_image_refs.objects.get_or_create(item=item, thumb10=document_thumb10)
            logger.debug(f'\nItem_image_refs: {item_image_refs}, created: {created}')

    def rec_image_cwd(self, item_id, STMP_2):
        for item_image in Item_image_refs.objects.select_related('item').filter(item__props__in=[Item.props.relevant | Item.props.from_cdw, Item.props.relevant | Item.props.from_pdf], item__STMP_2__value_str=STMP_2):
            _, created = Item_image_refs.objects.get_or_create(item_id=item_id, thumb_id=item_image.thumb_id, thumb10_id=item_image.thumb10_id)
            if created:
                logger1.debug(f'\nAdded: {item_image}')

    def del_blancks1(self, STMP_2):
        STMP_2_1 = ' '.join(STMP_2.split())
        if STMP_2_1 != STMP_2:
            return STMP_2_1
        return STMP_2

    def handle(self, *args, **options):

        logger.info(self.help)

        self.makeItem.meke_cdw(True)

        return
        # </editor-fold>

        # <editor-fold desc="Этап 2">
        self.pbar = tqdm(total=Pdfs.objects.filter(props=~Documents.props.beenItemed).count())

        STMP_1_type = Attr_type.objects.get(code='STMP_1')
        STMP_2_type = Attr_type.objects.get(code='STMP_2')

        with transaction.atomic():
            for document in Pdfs.objects.filter(props=~Documents.props.beenItemed):
                if document.file_document.lower().find('мусор') == -1:
                    # logger.debug(f'Iteming: {document}')

                    full_path = document.file_document
                    _, file_name = os.path.split(full_path)
                    file_name_part = file_name.split(' - ')
                    if len(file_name_part) == 2:

                        STMP_1, ext = os.path.splitext(file_name_part[1].strip())
                        STMP_2 = self.del_blancks1(file_name_part[0].strip())
                    else:
                        STMP_1 = str(file_name.strip()).replace('.pdf', '')
                        STMP_2 = STMP_1

                    args = dict(
                        STMP_1=STMP_1,
                        STMP_2=STMP_2,
                    )

                    cnt = 0
                    items = []
                    for item in Item.objects.filter(
                            STMP_1__value_str=args.get('STMP_1'),
                            STMP_2__value_str=args.get('STMP_2'),
                            props=Item.props.relevant
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
                            props=Item.props.relevant,
                            defaults=dict(document=document, props=Item.props.relevant | Item.props.from_pdf)
                        )

                        if created:
                            logger.debug(f'\nAdded: {item}')
                        else:
                            logger.debug('==============================================================================================================')

                        self.link_image_to_item(item)
                    else:
                        for item in items:
                            logger.debug(f'\nНайдено: элемент пришедший из {cnt + 1}-x источников : {item}')
                            self.link_image_to_item(item)

                    document.props |= Documents.props.beenItemed
                    document.save()

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        return
        # </editor-fold>

        self.pbar = tqdm(total=Spws.objects.filter(props=~Documents.props.beenItemed).count())

        # <editor-fold desc="Этап 3">
        with transaction.atomic():
            top_auto_level_type, _ = Attr_type.objects.get_or_create(code='top_auto_level')
            top_auto_level_attr, _ = Document_attributes.objects.get_or_create(attr_type=top_auto_level_type, value_str='Автоматически сгененрированный состав изделий')
            top_auto_level_item, _ = Item.objects.get_or_create(STMP_1=top_auto_level_attr, props=Item.props.relevant | Item.props.from_spw)
            item_refs, _ = Item_refs.objects.get_or_create(child=top_auto_level_item)

            for document in Spws.objects.filter(props=~Documents.props.beenItemed):
                # with transaction.atomic():
                if document.file_document.lower().find('мусор') == -1:
                    # logger.debug(f'Iteming: {document}')

                    STMP_1 = Spw_attrs.objects.all().get_attr(document=document, code='STMP_1')
                    STMP_2 = Spw_attrs.objects.all().get_attr(document=document, code='STMP_2')

                    if STMP_1 != None or STMP_2 != None:

                        kwargs = dict(
                            STMP_1_id=STMP_1.id if STMP_1 else None,
                            STMP_2_id=STMP_2.id if STMP_2 else None,
                            props=Item.props.relevant
                        )

                        parent, created = Item.objects.get_or_create(
                            **kwargs,
                            defaults=dict(document=document, props=Item.props.relevant | Item.props.from_spw))

                        if created:
                            item_refs = Item_refs.objects.create(parent=top_auto_level_item, child=parent)
                            logger.debug(f'\nAdded: {item_refs} as tpo level')

                        if kwargs.get('STMP_2__value_str') != None:
                            self.rec_image_cwd(parent.id, kwargs.get('STMP_2__value_str'))
                        self.link_image_to_item(parent)

                        query_spw = Spw_attrs.objects.filter(document=document, props=Document_attributes.relevant).order_by(*['position_in_document'])
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
                                            _document_attribute = Document_attributes.objects.get(attr_type=document_attribute.attr_type, value_str=SPC_CLM_MARK, props=document_attribute.props)
                                            Document_attr_cross.objects.filter(attribute=document_attribute).update(attribute=_document_attribute)
                                            setAttr(line_specification, 'SPC_CLM_MARK_ID', _document_attribute.id)
                                            document_attribute.delete()
                                        except Document_attributes.DoesNotExist:
                                            document_attribute.value_str = SPC_CLM_MARK
                                            document_attribute.save()
                                            logger1.debug(f'=================================================>>>>>> Uppdated: {SPC_CLM_MARK}')

                                elif isinstance(SPC_CLM_MARK, str):
                                    SPC_CLM_MARK_old = SPC_CLM_MARK

                                child_args = dict(
                                    STMP_1=SPC_CLM_NAME_ID,
                                    STMP_2=SPC_CLM_MARK_ID,
                                )

                                child, created = Item.objects.get_or_create(
                                    STMP_1_id=child_args.get('STMP_1'),
                                    STMP_2_id=child_args.get('STMP_2'),
                                    props__in=[Item.props.relevant, Item.props.relevant | Item.props.from_spw | Item.props.for_line],
                                    defaults=dict(document=document)
                                )

                                if created:
                                    if child.STMP_2 != None:
                                        self.rec_image_cwd(child.id, child.STMP_2.value_str)
                                    logger.debug(f'\nAdded: {child} as child')
                                else:
                                    logger.debug(f'\nNot Added: {child} as child')

                                item_refs, created = Item_refs.objects.get_or_create(parent=parent, child=child)
                                if created:
                                    logger.debug(f'\nAdded: {item_refs}')
                                else:
                                    logger.debug(f'\nNot Added: {item_refs}')

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

                                item_line, created = Item_line.objects.get_or_create(parent=parent, child=child, defaults=defaults)
                                if created:
                                    logger.debug(f'\nAdded: {item_line} as item_line')
                                else:
                                    logger.debug(f'\nNot Added: {item_line} as item_line')

                    else:
                        logger.debug(f'\nSTMP_1 and STMP_2 is None, document: {document}')
                        document.delete_soft()

                document.props |= Documents.props.beenItemed
                document.save()

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        logger.info("Загрузка выполнена.")
        # </editor-fold>

# with transaction.atomic():

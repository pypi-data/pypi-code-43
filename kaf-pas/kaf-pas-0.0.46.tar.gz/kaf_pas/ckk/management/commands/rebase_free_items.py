import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.kd.models.document_attributes import Document_attributes

logger = logging.getLogger(__name__)
logger1 = logging.getLogger(f'{__name__}_1')


class Command(BaseCommand):
    help = "Перенос чертежей в подпапку"

    def handle(self, *args, **options):

        logger.info(self.help)

        cdws_type, _ = Attr_type.objects.get_or_create(code='CDWS', defaults=dict(name='Чертежи'))
        cdws_attr, _ = Document_attributes.objects.get_or_create(attr_type=cdws_type, value_str='Автоматически закачанные чертежи')
        cdws_item, _ = Item.objects.get_or_create(STMP_1=cdws_attr, props=Item.props.from_cdw)

        spws_type, _ = Attr_type.objects.get_or_create(code='top_auto_level')
        spws_attr, _ = Document_attributes.objects.get_or_create(attr_type=spws_type, value_str='Автоматически сгененрированный состав изделий')
        spws_item, _ = Item.objects.get_or_create(STMP_1=spws_attr, props= Item.props.from_spw)

        cnt = 0

        for item in Item.objects.filter(props__in=[Item.props.from_cdw, Item.props.from_pdf, Item.props.from_spw]):
            try:
                Item_refs.objects.get(child=item)
            except Item_refs.MultipleObjectsReturned:
                ...
            except Item_refs.DoesNotExist:
                cnt += 1
                print(cnt)

        self.pbar = tqdm(total=cnt)

        with transaction.atomic():
            for item in Item.objects.filter(props__in=[Item.props.from_cdw, Item.props.from_pdf]):
                try:
                    Item_refs.objects.get(child=item)
                except Item_refs.MultipleObjectsReturned:
                    ...
                except Item_refs.DoesNotExist:
                    Item_refs.objects.get_or_create(child=item, parent=cdws_item)

                    if self.pbar:
                        self.pbar.update(1)

            for item in Item.objects.filter(props__in=[Item.props.from_spw]):
                try:
                    Item_refs.objects.get(child=item)
                except Item_refs.MultipleObjectsReturned:
                    ...
                except Item_refs.DoesNotExist:
                    Item_refs.objects.get_or_create(child=item, parent=spws_item)

                    if self.pbar:
                        self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        logger.info("Загрузка выполнена.")
        # </editor-fold>

# with transaction.atomic():

import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.ckk.models.item_view import Item_view
from kaf_pas.kd.models.document_attributes import Document_attributes

logger = logging.getLogger(__name__)
logger1 = logging.getLogger(f'{__name__}_1')


class Command(BaseCommand):
    help = "Перенос чертежей в подпапку"

    def handle(self, *args, **options):

        logger.info(self.help)

        self.pbar = tqdm(total=Item_view.objects.filter(parent_id__isnull=True, props__in=[Item.props.relevant | Item.props.from_cdw, Item.props.relevant | Item.props.from_pdf]).count())
        cdws_type, _ = Attr_type.objects.get_or_create(code='CDWS', defaults=dict(name='Чертежи'))
        cdws_attr, _ = Document_attributes.objects.get_or_create(attr_type=cdws_type, value_str='Автоматически закачанные чертежи')
        cdws_item, _ = Item.objects.get_or_create(STMP_1=cdws_attr, props=Item.props.relevant | Item.props.from_cdw)
        item_refs, _ = Item_refs.objects.get_or_create(child=cdws_item)

        with transaction.atomic():
            for item in Item_view.objects.filter(parent_id__isnull=True, props__in=[Item.props.relevant | Item.props.from_cdw, Item.props.relevant | Item.props.from_pdf]):
                res = Item_refs.objects.filter(parent_id__isnull=True, child_id=item.id).delete()
                item_refs, _ = Item_refs.objects.get_or_create(child_id=item.id, parent=cdws_item)

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        logger.info("Загрузка выполнена.")
        # </editor-fold>

# with transaction.atomic():

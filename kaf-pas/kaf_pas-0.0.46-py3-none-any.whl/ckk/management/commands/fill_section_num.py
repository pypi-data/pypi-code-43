import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.ckk.models.item_line import Item_line, Item_lineManager
from kaf_pas.kd.models.document_attributes import Document_attributes, Document_attributesManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Заполнение поля section_num"

    def handle(self, *args, **options):
        logger.info(self.help)

        self.pbar = tqdm(total=Item_line.objects.all().count())

        with transaction.atomic():
            for item in Item_line.objects.all():
                item.section_num = Item_lineManager.section_num(item.section)
                item.save()

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

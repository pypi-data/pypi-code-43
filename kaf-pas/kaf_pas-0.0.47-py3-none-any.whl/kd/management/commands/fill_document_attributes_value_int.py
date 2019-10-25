import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.kd.models.document_attributes import Document_attributes, Document_attributesManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Заполнение поля value_int"

    def handle(self, *args, **options):
        logger.info(self.help)

        self.pbar = tqdm(total=Document_attributes.objects.all().count())

        with transaction.atomic():
            for item in Document_attributes.objects.all():
                item.value_int = Document_attributesManager.to_int(item.value_str)
                item.save()

                if self.pbar:
                    self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

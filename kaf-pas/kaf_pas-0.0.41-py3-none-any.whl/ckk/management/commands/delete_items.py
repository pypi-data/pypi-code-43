import logging

from django.core.management import BaseCommand
from tqdm import tqdm

from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_view import Item_view
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.spws import Spws

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Удаление составов изделий"

    def handle(self, *args, **options):

        logger.info(self.help)

        self.pbar = tqdm(total=Documents.objects.filter(props=Documents.props.beenItemed).count())

        for spw in Documents.objects.filter(props=Documents.props.beenItemed):
            spw.props = Documents.props.relevant
            spw.save()

            if self.pbar:
                self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        self.pbar = tqdm(total=Item.objects.filter().count())

        for item in Item.objects.filter():
            item.delete()

            if self.pbar:
                self.pbar.update(1)

        if self.pbar:
            self.pbar.close()

        logger.info("Удаление выполнено.")
        # </editor-fold>

# with transaction.atomic():

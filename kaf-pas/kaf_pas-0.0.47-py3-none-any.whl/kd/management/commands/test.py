import logging

from django.core.management import BaseCommand

from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_view import Item_view

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование"

    def handle(self, *args, **options):
        logger.info(self.help)

        query = Item.objects.filter(props=Item.props.from_cdw)
        query = Item_view.objects.filter(from_cdw=True)
        for item in query:
            logger.debug(item)

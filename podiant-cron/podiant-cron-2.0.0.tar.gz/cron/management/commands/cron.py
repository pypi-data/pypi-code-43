from django.core.management.base import BaseCommand
from ... import scheduler, autodiscover
import logging


class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def handle(self, *args, **options):
        autodiscover()

        logger = logging.getLogger('podiant.cron')
        logger.debug('Starting clock')

        scheduler.start()

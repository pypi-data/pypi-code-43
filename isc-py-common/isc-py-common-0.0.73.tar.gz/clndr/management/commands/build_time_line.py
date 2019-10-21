import logging

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Создание модели календаря.'

    def handle(self, *args, **options):
        from clndr.time_line import Timeline

        logger.debug(self.help)

        shiftsList = Timeline(calendar_id=3, logger=logger).build()
        # shiftsList.write_2_file('dest_debug/shifts.js')
        # json = shiftsList.to_json()
        # print(len(json))


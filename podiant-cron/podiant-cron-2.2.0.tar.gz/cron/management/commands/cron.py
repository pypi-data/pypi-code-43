from django.core.management.base import BaseCommand
from logging import getLogger
from ...helpers import autodiscover, get_scheduler


class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def handle(self, *args, **options):
        logger = getLogger('podiant.cron')
        scheduler = get_scheduler()
        cleared = 0

        for job in scheduler.get_jobs():
            cleared += 1
            job.delete()

        if cleared:
            logger.debug(
                'Cleared %d job(s) from scheduler' % cleared
            )

        autodiscover(schedule=True)
        logger.debug('Running cron worker')
        scheduler.run()

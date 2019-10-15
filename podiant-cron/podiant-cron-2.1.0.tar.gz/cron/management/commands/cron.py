from django.core.management.base import BaseCommand
from logging import getLogger
from ...helpers import autodiscover, get_scheduler


class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def handle(self, *args, **options):
        logger = getLogger('podiant.cron')

        scheduler = get_scheduler()
        jobs = list(scheduler.get_jobs())

        if any(jobs):
            logger.debug(
                'Clearing %d job(s) from scheduler' % len(jobs)
            )

            for job in jobs:
                logger.debug('Deleting \'%s\'' % job.func_name)
                job.delete()

        autodiscover()

        logger.debug('Running cron worker')
        scheduler.run()

import time

from django.core.management.base import BaseCommand
from djmaplearn.models import Job


class Command(BaseCommand):
    help = 'Job daemon'

    def handle(self, *args, **options):
        while 1:
            for job in Job.objects.filter(job_status="Q").all():
                if job.treat():
                    self.stdout.write(
                        self.style.NOTICE('Job {} success'.format(job.pk)))
                else:
                    self.stdout.write(
                        self.style.ERROR('Job {} failed'.format(job.pk)))
            time.sleep(30)

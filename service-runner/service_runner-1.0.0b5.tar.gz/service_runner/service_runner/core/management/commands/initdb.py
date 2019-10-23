import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger('django')


class Command(BaseCommand):

    def init_user(self):
        users = User.objects.all()
        if users:
            logger.info('User table is not empty. skip')
            return
        logger.info('Create User `admin` and setup password `admin123`')

        user = User.objects.create_user(
            'admin', 'admin@service_runner.com', 'admin123')
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        logger.info('User `admin` created.')

    def handle(self, *args, **options):
        self.init_user()

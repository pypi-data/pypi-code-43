import os

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from aorta.client import AortaClient


class Command(BaseCommand):

    def add_arguments(self, parser):
        """Adds the arguments for the Aorta client to the management
        command.
        """
        parser.add_argument('--host', default=os.getenv('AORTA_CLIENT_HOST'))
        parser.add_argument('--port', type=int,
            default=os.getenv('AORTA_CLIENT_PORT') or 5672)
        parser.add_argument('--channel', type=str,
            default=os.getenv('AORTA_INGRESS_CHANNEL'))

    def handle(self, *args, **kwargs):
        AortaClient.run(**kwargs)

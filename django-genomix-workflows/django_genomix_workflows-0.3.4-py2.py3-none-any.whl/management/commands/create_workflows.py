from django.core.management import BaseCommand

from ... import services


class Command(BaseCommand):
    help = 'Create Tasks in Database'

    def add_arguments(self, parser):
        parser.add_argument('filename', help='Mapping between TestCode and details')

    def handle(self, *args, **options):
        filename = options['filename']
        services.load_workflows(filename=filename)

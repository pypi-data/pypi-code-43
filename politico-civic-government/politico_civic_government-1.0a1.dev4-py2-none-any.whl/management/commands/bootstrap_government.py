# Imports from Django.
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Calls all upstream bootstrap commands and government commands"

    def handle(self, *args, **options):
        print("Bootstrapping government")
        call_command("bootstrap_geography")
        call_command("bootstrap_jurisdictions")
        call_command("bootstrap_fed")
        call_command("bootstrap_offices")
        call_command("bootstrap_parties")

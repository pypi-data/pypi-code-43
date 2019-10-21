# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import Race
from tqdm import tqdm


# Imports from race_ratings.
from raceratings.management.commands.methods import BootstrapContentMethods


class Command(BaseCommand, BootstrapContentMethods):
    help = (
        "Bootstraps page content items for pages for all elections on an "
        "election day. Must be run AFTER bootstrap_election command."
    )

    def handle(self, *args, **options):
        print("Bootstrapping page content")
        self.bootstrap_homepage_content()
        for race in tqdm(Race.objects.filter(cycle__slug="2020")):
            self.bootstrap_race_content(race)
        print("Done.")

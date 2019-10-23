# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from geography.models import Division
from geography.models import DivisionLevel
from tqdm import tqdm
import us


# Imports from government.
from government.models import Jurisdiction


class Command(BaseCommand):
    help = (
        "Loads federal and state jurisdictions. Must be run AFTER the"
        "bootstrap_geography command."
    )

    def handle(self, *args, **options):
        print("Loading jurisdictions")
        USA = Division.objects.get(code="00", level__name="country")
        FED, created = Jurisdiction.objects.get_or_create(
            name="U.S. Federal Government", division=USA
        )
        state_level = DivisionLevel.objects.get(name="state")
        for state in tqdm(us.states.STATES):
            if str(state.fips) == "11":
                continue
            division = Division.objects.get(code=state.fips, level=state_level)
            name = "{} State Government".format(state.name)
            Jurisdiction.objects.get_or_create(
                name=name, division=division, parent=FED
            )
        self.stdout.write(self.style.SUCCESS("Done."))

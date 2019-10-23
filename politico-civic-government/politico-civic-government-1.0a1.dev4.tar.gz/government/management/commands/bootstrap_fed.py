# Imports from python.
import datetime


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from entity.models import Organization
from geography.models import Division


# Imports from government.
from government.models import Body
from government.models import Jurisdiction
from government.models import Office


class Command(BaseCommand):
    help = (
        "Loads basic structure of the federal governement. Must be run AFTER "
        "bootstrap_geography command."
    )

    def handle(self, *args, **options):
        print("Loading the fed")
        USA = Division.objects.get(code="00", level__name="country")
        FED, created = Jurisdiction.objects.get_or_create(
            name="U.S. Federal Government", division=USA
        )
        congress, created = Organization.objects.update_or_create(
            name="United States Congress",
            defaults={"founding_date": datetime.date(1789, 3, 4)},
        )
        senate, created = Organization.objects.update_or_create(
            name="United States Senate",
            parent=congress,
            defaults={
                "links": ["https://www.senate.gov/"],
                "founding_date": datetime.date(1789, 3, 4),
            },
        )
        house, created = Organization.objects.update_or_create(
            name="United States House of Representatives",
            parent=congress,
            defaults={
                "links": ["https://www.house.gov/"],
                "founding_date": datetime.date(1789, 3, 4),
            },
        )
        Body.objects.get_or_create(
            slug="senate",
            organization=senate,
            jurisdiction=FED,
            label="U.S. Senate",
            short_label="Senate",
        )
        Body.objects.get_or_create(
            slug="house",
            organization=house,
            jurisdiction=FED,
            label="U.S. House of Representatives",
            short_label="U.S. House",
        )

        self.stdout.write(self.style.SUCCESS("Done."))

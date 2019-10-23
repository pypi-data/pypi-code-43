# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from elections import ElectionYear
from geography.models import Division
from geography.models import DivisionLevel
from tqdm import tqdm


# Imports from government.
from government.models import Body
from government.models import Jurisdiction
from government.models import Office


class Command(BaseCommand):
    help = "Creates federal offices"

    fed = Jurisdiction.objects.get(name="U.S. Federal Government")

    def build_house_offices(self):
        election_year = ElectionYear(2020)
        house_seats = election_year.seats.house
        division_level = DivisionLevel.objects.get(name="district")
        body = Body.objects.get(slug="house", jurisdiction=self.fed)
        for seat in tqdm(house_seats):
            division = Division.objects.get(
                level=division_level,
                parent__code=seat.state.fips,
                code="00" if not seat.district else seat.district.zfill(2),
            )

            Office.objects.update_or_create(
                jurisdiction=self.fed,
                division=division,
                body=body,
                senate_class=None,
                defaults={"name": seat.__str__(), "label": seat.__str__()},
            )

    def build_senate_offices(self, year):
        def translate_senate_class(s):
            if s == "I":
                return "1"
            if s == "II":
                return "2"
            if s == "III":
                return "3"
            return s

        election_year = ElectionYear(year)
        senate_seats = election_year.seats.senate
        division_level = DivisionLevel.objects.get(name="state")
        body = Body.objects.get(slug="senate", jurisdiction=self.fed)
        for seat in tqdm(senate_seats):
            division = Division.objects.get(
                level=division_level, code=seat.state.fips
            )
            Office.objects.update_or_create(
                jurisdiction=self.fed,
                division=division,
                body=body,
                senate_class=translate_senate_class(seat.senate_class),
                defaults={"name": seat.__str__(), "label": seat.__str__()},
            )

    def build_governorships(self):
        state_level = DivisionLevel.objects.get(name="state")

        state_jurisdictions = Jurisdiction.objects.filter(
            division__level=state_level
        )

        print("Loading governorships")
        for jurisdiction in tqdm(state_jurisdictions):
            name = "{0} Governor".format(jurisdiction.division.name)

            Office.objects.get_or_create(
                name=name,
                label=name,
                jurisdiction=jurisdiction,
                division=jurisdiction.division,
            )

    def build_presidency(self):
        USA = Division.objects.get(code="00", level__name="country")

        print("Loading presidency")

        Office.objects.get_or_create(
            slug="president",
            name="President of the United States",
            label="U.S. President",
            short_label="President",
            jurisdiction=self.fed,
            division=USA,
        )

    def handle(self, *args, **options):
        print("Loading offices")

        self.build_house_offices()
        self.build_senate_offices(2018)
        self.build_senate_offices(2020)
        self.build_senate_offices(2022)
        self.build_governorships()
        self.build_presidency()

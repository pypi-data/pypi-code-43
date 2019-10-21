# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import ElectionCycle
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
from government.models import Jurisdiction
from government.models import Office
from elections import ElectionYear
import us


# Imports from race_ratings.
from raceratings.constants import ACCEPTED_GOVERNMENT_BODIES
from raceratings.constants import ELECTORAL_COLLEGE_BODY
from raceratings.constants import STATE_GOVERNORS_BODY
from raceratings.constants import US_SENATE_BODY
from raceratings.constants import US_HOUSE_BODY


class Command(BaseCommand):
    help = (
        "Given a year, create all electoral races "
        "(in various government bodies) "
        "that we will rate this year."
    )

    bodies_to_create = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            required=True,
            help="The year for which we'll be creating races.",
        )

        parser.add_argument(
            "args",
            metavar="government_bodies",
            nargs="*",
            help="".join(
                [
                    "A list of which government bodies should be loaded. ",
                    "These may be any of ",
                    "'{}' or '{}'".format(
                        "', '".join(ACCEPTED_GOVERNMENT_BODIES[:-1]),
                        ACCEPTED_GOVERNMENT_BODIES[-1],
                    )
                    if len(ACCEPTED_GOVERNMENT_BODIES) > 1
                    else "'{}'".format(ACCEPTED_GOVERNMENT_BODIES[0]),
                    ".",
                ]
            ),
        )

    fed = Jurisdiction.objects.get(name="U.S. Federal Government")

    def create_electoral_college_races(self):
        new_statewide_races = []
        existing_statewide_races = []

        new_per_district_races = []
        existing_per_district_races = []

        electoral_zones = (
            self.election_year_data.federal.executive.chief.electoral_votes
        )

        division = Division.objects.get(
            level__name=DivisionLevel.COUNTRY, code="00"
        )
        office = Office.objects.get(
            body=None, division=division, slug="president"
        )

        for statewide_zone in electoral_zones.statewide:
            state_division = Division.objects.get(
                level__name=DivisionLevel.STATE, code=statewide_zone.state.fips
            )
            race, created = Race.objects.get_or_create(
                office=office,
                cycle=self.cycle,
                division=state_division,
                special=False,
            )

            if created:
                new_statewide_races.append(race)
            else:
                existing_statewide_races.append(race)

        for per_district_zone in electoral_zones.by_district:
            district_division = Division.objects.get(
                level__name=DivisionLevel.DISTRICT,
                parent__code=per_district_zone.state.fips,
                code=per_district_zone.district.zfill(2),
            )
            race, created = Race.objects.get_or_create(
                office=office,
                cycle=self.cycle,
                division=district_division,
                special=False,
            )

            if created:
                new_per_district_races.append(race)
            else:
                existing_per_district_races.append(race)

        return (
            new_statewide_races,
            existing_statewide_races,
            new_per_district_races,
            existing_per_district_races,
        )

    def create_senate_races(self):
        new_races = []
        existing_races = []

        def translate_senate_class(s):
            if s == "I":
                return "1"
            if s == "II":
                return "2"
            if s == "III":
                return "3"
            return s

        senate_seats = self.election_year_data.federal.legislative.seats.senate
        body = Body.objects.get(slug="senate", jurisdiction=self.fed)
        for seat in senate_seats:
            division = Division.objects.get(
                level__name=DivisionLevel.STATE, code=seat.state.fips
            )
            office = Office.objects.get(
                body=body,
                division=division,
                senate_class=translate_senate_class(seat.senate_class),
            )
            race, created = Race.objects.get_or_create(
                office=office, cycle=self.cycle, special=seat.special
            )

            if created:
                new_races.append(race)
            else:
                existing_races.append(race)

        return new_races, existing_races

    def create_house_races(self):
        new_races = []
        existing_races = []

        house_seats = self.election_year_data.federal.legislative.seats.house
        body = Body.objects.get(slug="house", jurisdiction=self.fed)
        for seat in house_seats:
            division = Division.objects.get(
                level__name=DivisionLevel.DISTRICT,
                parent__code=seat.state.fips,
                code="00" if not seat.district else seat.district.zfill(2),
            )
            office = Office.objects.get(
                body=body, division=division, senate_class=None
            )
            race, created = Race.objects.get_or_create(
                office=office, cycle=self.cycle, special=seat.special
            )

            if created:
                new_races.append(race)
            else:
                existing_races.append(race)

        return new_races, existing_races

    def create_gubernatorial_races(self):
        new_races = []
        existing_races = []

        governor_seats = [
            state.executive.chief
            for state in self.election_year_data.states
            if state.executive.chief
        ]
        for seat in governor_seats:
            division = Division.objects.get(
                level__name=DivisionLevel.STATE, code=seat.state.fips
            )
            office = Office.objects.get(
                division=division, body=None, senate_class=None
            )
            race, created = Race.objects.get_or_create(
                office=office, cycle=self.cycle
            )

            if created:
                new_races.append(race)
            else:
                existing_races.append(race)

        return new_races, existing_races

    def handle(self, *government_bodies, **options):
        # If no government bodies were explicitly stated, create all of them.
        if government_bodies:
            self.bodies_to_create = [
                body
                for body in government_bodies
                if body in ACCEPTED_GOVERNMENT_BODIES
            ]

        if not self.bodies_to_create:
            self.bodies_to_create = ACCEPTED_GOVERNMENT_BODIES

        self.year = options["year"]

        self.election_year_data = ElectionYear(self.year)
        self.cycle = ElectionCycle.objects.get_or_create(name=self.year)[0]

        if ELECTORAL_COLLEGE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating electoral college races for {}...".format(
                        self.year
                    )
                )
            )

            (
                created_state_races,
                unmodified_state_races,
                created_district_races,
                unmodified_district_races,
            ) = self.create_electoral_college_races()

            self.stdout.write(
                "  ✅   Created {} new per-state {}.".format(
                    len(created_state_races),
                    "races" if len(created_state_races) != 1 else "race",
                )
            )
            self.stdout.write(
                "  ℹ️   {} per-state {} existed and {} modified.".format(
                    len(unmodified_state_races),
                    "races" if len(unmodified_state_races) != 1 else "race",
                    "weren't"
                    if len(unmodified_state_races) != 1
                    else "wasn't",
                )
            )
            self.stdout.write(
                "  ✅   Created {} new per-district {}.".format(
                    len(created_district_races),
                    "races" if len(created_district_races) != 1 else "race",
                )
            )
            self.stdout.write(
                "  ℹ️   {} per-district {} existed and {} modified.".format(
                    len(unmodified_district_races),
                    "races" if len(unmodified_district_races) != 1 else "race",
                    "weren't"
                    if len(unmodified_district_races) != 1
                    else "wasn't",
                )
            )
            self.stdout.write("")

        if US_SENATE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating U.S. Senate races for {}...".format(self.year)
                )
            )

            created_races, unmodified_races = self.create_senate_races()

            self.stdout.write(
                "  ✅   Created {} new {}.".format(
                    len(created_races),
                    "races" if len(created_races) != 1 else "race",
                )
            )
            self.stdout.write(
                "  ℹ️   {} {} existed and {} modified.".format(
                    len(unmodified_races),
                    "races" if len(unmodified_races) != 1 else "race",
                    "weren't" if len(unmodified_races) != 1 else "wasn't",
                )
            )
            self.stdout.write("")

        if US_HOUSE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating U.S. House races for {}...".format(self.year)
                )
            )

            created_races, unmodified_races = self.create_house_races()

            self.stdout.write(
                "  ✅   Created {} new {}.".format(
                    len(created_races),
                    "races" if len(created_races) != 1 else "race",
                )
            )
            self.stdout.write(
                "  ℹ️   {} {} existed and {} modified.".format(
                    len(unmodified_races),
                    "races" if len(unmodified_races) != 1 else "race",
                    "weren't" if len(unmodified_races) != 1 else "wasn't",
                )
            )
            self.stdout.write("")

        if STATE_GOVERNORS_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating governors' races for {}...".format(self.year)
                )
            )

            created_races, unmodified_races = self.create_gubernatorial_races()

            self.stdout.write(
                "  ✅   Created {} new {}.".format(
                    len(created_races),
                    "races" if len(created_races) != 1 else "race",
                )
            )
            self.stdout.write(
                "  ℹ️   {} {} existed and {} modified.".format(
                    len(unmodified_races),
                    "races" if len(unmodified_races) != 1 else "race",
                    "weren't" if len(unmodified_races) != 1 else "wasn't",
                )
            )
            self.stdout.write("")

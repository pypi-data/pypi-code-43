# Imports from python.
import csv
import os


# Imports from Django.
from django.core.management.base import BaseCommand
from django.db.models import signals


# Imports from other dependencies.
from election.models import ElectionCycle
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
from government.models import Jurisdiction
from government.models import Office
import us


# Imports from race_ratings.
from raceratings.conf import settings
from raceratings.constants import ACCEPTED_GOVERNMENT_BODIES
from raceratings.constants import ELECTORAL_COLLEGE_BODY
from raceratings.constants import RATING_CATEGORIES
from raceratings.constants import STATE_GOVERNORS_BODY
from raceratings.constants import US_SENATE_BODY
from raceratings.constants import US_HOUSE_BODY
from raceratings.models import Author
from raceratings.models import Category
from raceratings.models import RaceRating
from raceratings.managers import TempDisconnectSignal
from raceratings.signals import race_rating_save


class Command(BaseCommand):
    help = (
        "Load one or more CSV files of race ratings. "
        "Each file will contain ratings for one government body."
    )

    bodies_to_create = []

    def create_categories(self):
        dem_pattern = ["-D", " Democrat"]
        gop_pattern = ["-R", " Republican"]

        created_categories = []
        existing_categories = []

        for i, category in enumerate(RATING_CATEGORIES):
            category, created = Category.objects.get_or_create(
                label=category.replace(*dem_pattern).replace(*gop_pattern),
                short_label=category,
                order=(i + 1),
            )

            if created:
                created_categories.append(category)
            else:
                existing_categories.append(category)

        return created_categories, existing_categories

    def load_electoral_college_ratings(self):
        created_ratings = []
        existing_ratings = []

        us_division = Division.objects.get(
            level__name=DivisionLevel.COUNTRY, code="00"
        )

        office = Office.objects.get(
            body=None, division=us_division, slug="president"
        )

        with open(self.electoral_college_file, "r") as input_file:
            for raw_rating in csv.DictReader(input_file):
                state = us.states.lookup(raw_rating["state"])

                district = raw_rating["district"]

                if district:
                    division = Division.objects.get(
                        level__name=DivisionLevel.DISTRICT,
                        parent__code=state.fips,
                        code=district.zfill(2),
                    )
                else:
                    division = Division.objects.get(
                        level__name=DivisionLevel.STATE, code=state.fips
                    )

                race = Race.objects.get(
                    office=office,
                    cycle=self.cycle,
                    division=division,
                    special=False,
                )

                category = Category.objects.get(
                    short_label=raw_rating["rating"]
                )

                rating, created = RaceRating.objects.get_or_create(
                    race=race, author=self.author, category=category
                )

                if created:
                    created_ratings.append(rating)
                else:
                    existing_ratings.append(rating)

        return created_ratings, existing_ratings

    def load_senate_ratings(self):
        body = Body.objects.get(slug="senate", jurisdiction=self.fed)

        created_ratings = []
        existing_ratings = []

        with open(self.us_senate_file, "r") as input_file:
            for rating in csv.DictReader(input_file):
                state = us.states.lookup(rating["state"])
                special = rating["special"].lower() == "true"

                division = Division.objects.get(
                    level__name=DivisionLevel.STATE, code=state.fips
                )

                office = Office.objects.get(
                    body=body,
                    division=division,
                    senate_class=rating["senate_class"],
                )

                race = Race.objects.get(
                    office=office, cycle=self.cycle, special=special
                )

                category = Category.objects.get(short_label=rating["rating"])

                rating, created = RaceRating.objects.get_or_create(
                    race=race, author=self.author, category=category
                )

                if created:
                    created_ratings.append(rating)
                else:
                    existing_ratings.append(rating)

        return created_ratings, existing_ratings

    def load_house_ratings(self):
        body = Body.objects.get(slug="house", jurisdiction=self.fed)

        created_ratings = []
        existing_ratings = []

        with open(self.us_house_file, "r") as input_file:
            for rating in csv.DictReader(input_file):
                state = us.states.lookup(rating["state"])

                if rating["district"] == "":
                    district_code = "00"
                else:
                    district_code = rating["district"].zfill(2)

                special = rating["special"].lower() == "true"

                division = Division.objects.get(
                    level__name=DivisionLevel.DISTRICT,
                    parent__code=state.fips,
                    code=district_code,
                )

                office = Office.objects.get(
                    body=body, division=division, senate_class=None
                )

                race = Race.objects.get(
                    office=office, cycle=self.cycle, special=special
                )

                category = Category.objects.get(short_label=rating["rating"])

                rating, created = RaceRating.objects.get_or_create(
                    race=race, author=self.author, category=category
                )

                if created:
                    created_ratings.append(rating)
                else:
                    existing_ratings.append(rating)

        return created_ratings, existing_ratings

    def load_gubernatorial_ratings(self):
        created_ratings = []
        existing_ratings = []

        with open(self.governor_file, "r") as input_file:
            for rating in csv.DictReader(input_file):
                state = us.states.lookup(rating["state"])
                special = rating["special"].lower() == "true"

                division = Division.objects.get(
                    level__name=DivisionLevel.STATE, code=state.fips
                )

                office = Office.objects.get(
                    division=division, body=None, senate_class=None
                )

                race = Race.objects.get(
                    office=office, cycle=self.cycle, special=special
                )

                category = Category.objects.get(short_label=rating["rating"])

                rating, created = RaceRating.objects.get_or_create(
                    race=race, author=self.author, category=category
                )

                if created:
                    created_ratings.append(rating)
                else:
                    existing_ratings.append(rating)

        return created_ratings, existing_ratings

    def add_arguments(self, parser):
        parser.add_argument(
            "--year", required=True, help="The year for these ratings."
        )

        parser.add_argument(
            "--author",
            required=True,
            help=(
                "Who should have the credit/byline for these ratings? "
                "Express this as 'Last, First'."
            ),
        )

        parser.add_argument(
            "args",
            metavar="government_bodies",
            nargs="*",
            help="".join(
                [
                    "Which government bodies' files should be created. ",
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

        parser.add_argument(
            "--input-directory",
            default=getattr(settings, "SCRATCH_FILE_DIR", ""),
            help="Where to place the output files.",
        )

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

        author_name_raw = [
            _.strip(" ") for _ in options["author"].lower().split(",")
        ]
        author_formatted = dict(
            first_name=" ".join(
                [_.capitalize() for _ in author_name_raw[1].split(" ")]
            ),
            last_name=author_name_raw[0].capitalize(),
        )

        self.author, created = Author.objects.get_or_create(**author_formatted)

        if created:
            self.stdout.write(
                self.style.HTTP_SERVER_ERROR(
                    " ✅ Created race rating author '{} {}'.".format(
                        author_formatted["first_name"],
                        author_formatted["last_name"],
                    )
                )
            )
            self.stdout.write("")

        self.year = options["year"]
        self.input_directory = options["input_directory"]

        self.cycle = ElectionCycle.objects.get_or_create(name=self.year)[0]
        self.fed = Jurisdiction.objects.get(name="U.S. Federal Government")

        kwargs = {
            "signal": signals.post_save,
            "receiver": race_rating_save,
            "sender": RaceRating,
        }

        with TempDisconnectSignal(**kwargs):
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Syncing rating categories...".format(self.year)
                )
            )
            new_categories, existing_categories = self.create_categories()
            self.stdout.write(
                "  ✅   Created {} new {}.".format(
                    len(new_categories),
                    "categories" if len(new_categories) != 1 else "category",
                )
            )
            self.stdout.write(
                "  ℹ️   {} {} existed and {} modified.".format(
                    len(existing_categories),
                    "categories"
                    if len(existing_categories) != 1
                    else "category",
                    "weren't" if len(existing_categories) != 1 else "wasn't",
                )
            )
            self.stdout.write("")

            if ELECTORAL_COLLEGE_BODY in self.bodies_to_create:
                self.electoral_college_file = os.path.join(
                    self.input_directory, "electoral-college.csv"
                )
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "Loading electoral college ratings from {}...".format(
                            self.electoral_college_file
                        )
                    )
                )
                new_ratings, existing_ratings = (
                    self.load_electoral_college_ratings()
                )
                self.stdout.write(
                    "  ✅   Created {} new {}.".format(
                        len(new_ratings),
                        "ratings" if len(new_ratings) != 1 else "rating",
                    )
                )
                self.stdout.write(
                    "  ℹ️   {} {} existed and {} modified.".format(
                        len(existing_ratings),
                        "ratings" if len(existing_ratings) != 1 else "rating",
                        "weren't" if len(existing_ratings) != 1 else "wasn't",
                    )
                )
                self.stdout.write("")

            if US_SENATE_BODY in self.bodies_to_create:
                self.us_senate_file = os.path.join(
                    self.input_directory, "senate.csv"
                )
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "Loading U.S. Senate ratings from {}...".format(
                            self.us_senate_file
                        )
                    )
                )
                new_ratings, existing_ratings = self.load_senate_ratings()
                self.stdout.write(
                    "  ✅   Created {} new {}.".format(
                        len(new_ratings),
                        "ratings" if len(new_ratings) != 1 else "rating",
                    )
                )
                self.stdout.write(
                    "  ℹ️   {} {} existed and {} modified.".format(
                        len(existing_ratings),
                        "ratings" if len(existing_ratings) != 1 else "rating",
                        "weren't" if len(existing_ratings) != 1 else "wasn't",
                    )
                )
                self.stdout.write("")

            if US_HOUSE_BODY in self.bodies_to_create:
                self.us_house_file = os.path.join(
                    self.input_directory, "house.csv"
                )
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "Loading U.S. House ratings from {}...".format(
                            self.us_house_file
                        )
                    )
                )
                new_ratings, existing_ratings = self.load_house_ratings()
                self.stdout.write(
                    "  ✅   Created {} new {}.".format(
                        len(new_ratings),
                        "ratings" if len(new_ratings) != 1 else "rating",
                    )
                )
                self.stdout.write(
                    "  ℹ️   {} {} existed and {} modified.".format(
                        len(existing_ratings),
                        "ratings" if len(existing_ratings) != 1 else "rating",
                        "weren't" if len(existing_ratings) != 1 else "wasn't",
                    )
                )
                self.stdout.write("")

            if STATE_GOVERNORS_BODY in self.bodies_to_create:
                self.governor_file = os.path.join(
                    self.input_directory, "governor.csv"
                )
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "Loading governors' ratings from {}...".format(
                            self.governor_file
                        )
                    )
                )
                new_ratings, existing_ratings = (
                    self.load_gubernatorial_ratings()
                )
                self.stdout.write(
                    "  ✅   Created {} new {}.".format(
                        len(new_ratings),
                        "ratings" if len(new_ratings) != 1 else "rating",
                    )
                )
                self.stdout.write(
                    "  ℹ️   {} {} existed and {} modified.".format(
                        len(existing_ratings),
                        "ratings" if len(existing_ratings) != 1 else "rating",
                        "weren't" if len(existing_ratings) != 1 else "wasn't",
                    )
                )
                self.stdout.write("")

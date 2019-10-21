# Imports from python.
import csv
import os


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import ElectionCycle
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Jurisdiction
import us


# Imports from race_ratings.
from raceratings.conf import settings
from raceratings.constants import ACCEPTED_GOVERNMENT_BODIES
from raceratings.constants import ELECTORAL_COLLEGE_BODY
from raceratings.constants import RATING_CATEGORIES
from raceratings.constants import STATE_GOVERNORS_BODY
from raceratings.constants import US_SENATE_BODY
from raceratings.constants import US_HOUSE_BODY


class Command(BaseCommand):
    help = (
        "Given a year, create blank CSV templates for all races we will be "
        "rating that year. "
        "Generates one file for each government body."
    )

    bodies_to_create = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            required=True,
            help="The year for which we'll be rating races.",
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
            "--output-directory",
            default=getattr(settings, "SCRATCH_FILE_DIR", ""),
            help="Where to place the output files.",
        )

    def generate_csv_data(self, race_list, **kwargs):
        if "state_field" not in kwargs:
            raise ValueError('Missing required argument "state_field".')

        state_field = kwargs.get("state_field")
        district_field = kwargs.get("district_field", None)
        additional_fields = kwargs.get("additional_fields", {})

        if district_field:
            raw_rows = race_list.values(
                *[
                    state_field,
                    district_field,
                    *[k for k, v in additional_fields.items() if k != ""],
                ]
            )

            formatted_rows = [
                {
                    "state": us.states.lookup(row[state_field]).abbr,
                    "district": int(row[district_field])
                    if row[district_field] != "00"
                    else None,
                    **{
                        v: row[k]
                        for k, v in additional_fields.items()
                        if k != ""
                    },
                    **{
                        v: None
                        for k, v in additional_fields.items()
                        if k == ""
                    },
                    "rating": RATING_CATEGORIES[i % len(RATING_CATEGORIES)],
                    "description": "",
                }
                for i, row in enumerate(raw_rows)
            ]

            header_rows = ["state", "district"]
        else:
            raw_rows = race_list.values(
                *[
                    state_field,
                    *[k for k, v in additional_fields.items() if k != ""],
                ]
            )

            formatted_rows = [
                {
                    "state": us.states.lookup(row[state_field]).abbr,
                    **{
                        v: row[k]
                        for k, v in additional_fields.items()
                        if k != ""
                    },
                    **{
                        v: None
                        for k, v in additional_fields.items()
                        if k == ""
                    },
                    "rating": RATING_CATEGORIES[i % len(RATING_CATEGORIES)],
                    "description": "",
                }
                for i, row in enumerate(raw_rows)
            ]

            header_rows = ["state"]

        header_rows.extend(
            [
                *[v for k, v in additional_fields.items() if k != ""],
                "rating",
                "description",
            ]
        )

        return header_rows, formatted_rows

    def export_ratings(self, header_fields, data_rows, output_file):
        with open(
            os.path.join(self.output_directory, output_file), "w"
        ) as csv_output_file:
            writer = csv.DictWriter(csv_output_file, fieldnames=header_fields)
            writer.writeheader()
            for row in data_rows:
                writer.writerow(row)

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
        self.output_directory = os.path.join(
            options["output_directory"], self.year
        )

        os.makedirs(self.output_directory, exist_ok=True)

        self.cycle = ElectionCycle.objects.get_or_create(name=self.year)[0]
        self.fed = Jurisdiction.objects.get(name="U.S. Federal Government")

        if ELECTORAL_COLLEGE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "".join(
                        [
                            "Creating template for {} ".format(self.year),
                            "electoral college ratings...",
                        ]
                    )
                )
            )
            races_to_rate = Race.objects.filter(
                cycle=self.cycle,
                office__jurisdiction=self.fed,
                office__body__isnull=True,
            )

            statewide_races = races_to_rate.filter(
                division__level__name=DivisionLevel.STATE
            )

            statewide_csv_header, statewide_csv_rows = self.generate_csv_data(
                statewide_races,
                state_field="division__code",
                additional_fields={"": "district"},
            )

            by_district_races = races_to_rate.exclude(
                division__level__name=DivisionLevel.STATE
            )

            district_csv_header, by_district_csv_rows = self.generate_csv_data(
                by_district_races,
                state_field="division__parent__code",
                district_field="division__code",
            )

            all_ratings = [*statewide_csv_rows, *by_district_csv_rows]

            self.export_ratings(
                district_csv_header, all_ratings, "electoral-college.csv"
            )

            self.stdout.write(
                "".join(
                    [
                        "  ✅   Exported template with ",
                        "{} electoral college {}.".format(
                            len(all_ratings),
                            "races" if len(all_ratings) != 1 else "race",
                        ),
                    ]
                )
            )

            self.stdout.write(
                self.style.SQL_KEYWORD(
                    "      📂  File location: "
                    "'{}/electoral-college.csv'".format(self.output_directory)
                )
            )

            self.stdout.write("")

        if US_SENATE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating template for {} U.S. Senate ratings...".format(
                        self.year
                    )
                )
            )
            races_to_rate = Race.objects.filter(
                cycle=self.cycle,
                office__jurisdiction=self.fed,
                office__body__slug="senate",
            )

            csv_header, csv_rows = self.generate_csv_data(
                races_to_rate,
                state_field="office__division__code",
                additional_fields={
                    "office__senate_class": "senate_class",
                    "special": "special",
                },
            )

            self.export_ratings(csv_header, csv_rows, "senate.csv")

            self.stdout.write(
                "  ✅   Exported template with {} U.S. Senate {}.".format(
                    len(csv_rows), "races" if len(csv_rows) != 1 else "race"
                )
            )

            self.stdout.write(
                self.style.SQL_KEYWORD(
                    "      📂  File location: "
                    "'{}/senate.csv'".format(self.output_directory)
                )
            )

            self.stdout.write("")

        if US_HOUSE_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating template for {} U.S. House ratings...".format(
                        self.year
                    )
                )
            )
            races_to_rate = Race.objects.filter(
                cycle=self.cycle,
                office__jurisdiction=self.fed,
                office__body__slug="house",
            )

            csv_header, csv_rows = self.generate_csv_data(
                races_to_rate,
                state_field="office__division__parent__code",
                district_field="office__division__code",
                additional_fields={"special": "special"},
            )

            self.export_ratings(csv_header, csv_rows, "house.csv")

            self.stdout.write(
                "  ✅   Exported template with {} U.S. House {}.".format(
                    len(csv_rows), "races" if len(csv_rows) != 1 else "race"
                )
            )
            self.stdout.write(
                self.style.SQL_KEYWORD(
                    "      📂  File location: "
                    "'{}/house.csv'".format(self.output_directory)
                )
            )

            self.stdout.write("")

        if STATE_GOVERNORS_BODY in self.bodies_to_create:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    "Creating template for {} gubernatorial ratings...".format(
                        self.year
                    )
                )
            )
            races_to_rate = Race.objects.filter(
                cycle=self.cycle, office__body__isnull=True
            ).exclude(office__jurisdiction=self.fed)

            csv_header, csv_rows = self.generate_csv_data(
                races_to_rate,
                state_field="office__division__code",
                additional_fields={"special": "special"},
            )

            self.export_ratings(csv_header, csv_rows, "governor.csv")

            self.stdout.write(
                "  ✅   Exported template with {} gubernatorial {}.".format(
                    len(csv_rows), "races" if len(csv_rows) != 1 else "race"
                )
            )

            self.stdout.write(
                self.style.SQL_KEYWORD(
                    "      📂  File location: "
                    "'{}/governor.csv'".format(self.output_directory)
                )
            )

            self.stdout.write("")

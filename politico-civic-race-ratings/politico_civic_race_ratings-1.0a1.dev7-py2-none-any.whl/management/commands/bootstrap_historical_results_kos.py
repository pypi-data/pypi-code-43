# Imports from python.
import csv
import os


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
from tqdm import tqdm
from tqdm._utils import _term_move_up
import us


# Imports from race_ratings.
from raceratings.models import DataProfile


class Command(BaseCommand):
    help = "Load historical results from Daily Kos."

    TQDM_PREFIX = _term_move_up() + "\r"

    def read_csv(self, filepath):
        BASE_PATH = "../../bin/historical-results/csv/daily_kos/"
        self.cmd_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(self.cmd_path, BASE_PATH, filepath)) as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def handle(self, *args, **options):
        data = self.read_csv("2008-2016-president-by-district.csv")

        for d in tqdm(data):
            postal_code, district_code = d["cd"].split("-")
            state_fips = us.states.lookup(postal_code).fips

            DISTRICT = Division.objects.get(
                code="00" if district_code == "AL" else district_code,
                parent__code=state_fips,
                level__name=DivisionLevel.DISTRICT,
            )
            tqdm.write(self.TQDM_PREFIX + ">> {}           ".format(DISTRICT))
            HOUSE = Body.objects.get(slug="house")
            RACE = Race.objects.get(
                cycle__slug="2018",
                office__division=DISTRICT,
                office__body=HOUSE,
                special=False,
            )
            data_profile, created = DataProfile.objects.get_or_create(
                race=RACE, defaults={"data": {}}
            )
            new_data = data_profile.data
            new_data["historicalResults"]["president"] = [
                {
                    "year": "2008",
                    "dem": {"votePct": round(float(d["2008_d"]) / 100, 4)},
                    "gop": {"votePct": round(float(d["2008_r"]) / 100, 4)},
                    "winner": "dem"
                    if float(d["2008_d"]) > float(d["2008_r"])
                    else "gop",
                },
                {
                    "year": "2012",
                    "dem": {"votePct": round(float(d["2012_d"]) / 100, 4)},
                    "gop": {"votePct": round(float(d["2012_r"]) / 100, 4)},
                    "winner": "dem"
                    if float(d["2012_d"]) > float(d["2012_r"])
                    else "gop",
                },
                {
                    "year": "2016",
                    "dem": {"votePct": round(float(d["2016_d"]) / 100, 4)},
                    "gop": {"votePct": round(float(d["2016_r"]) / 100, 4)},
                    "winner": "dem"
                    if float(d["2016_d"]) > float(d["2016_r"])
                    else "gop",
                },
            ]
            DataProfile.objects.update_or_create(
                race=RACE, defaults={"data": new_data}
            )

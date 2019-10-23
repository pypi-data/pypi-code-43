# Imports from python.
from collections import defaultdict
import csv
from itertools import groupby
import os


# Imports from Django.
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
import requests
from tqdm import tqdm
from tqdm._utils import _term_move_up


# Imports from race_ratings.
from raceratings.models import DataProfile


class Command(BaseCommand):
    help = "Load historical results from MIT election lab."

    TQDM_PREFIX = _term_move_up() + "\r"

    def initialize_standardizer(self):
        BASE_PATH = "../../bin/historical-results/csv/mit_election_lab/"
        with open(
            os.path.join(self.cmd_path, BASE_PATH, "party-standardizer.csv")
        ) as f:
            reader = csv.DictReader(f)
            self.party_standards = [row for row in reader]

    def standard_party(self, row):
        for standard in self.party_standards:
            matches = []
            for key, value in standard.items():
                if key == "STANDARDIZED_PARTY":
                    continue
                if not value:  # skip empty values
                    continue
                if row[key] == value:
                    matches.append(True)
                else:
                    matches.append(False)
            if False not in matches:
                return standard["STANDARDIZED_PARTY"]
        return row["party"]

    def read_csv(self, filepath):
        BASE_PATH = "../../bin/historical-results/csv/mit_election_lab/"
        with open(os.path.join(self.cmd_path, BASE_PATH, filepath)) as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def download_csv(self, filepath):
        GITHUB_BASE = (
            "https://raw.githubusercontent.com/"
            "The-Politico/mit-elections-data/master/"
        )
        BASE_PATH = "../../bin/historical-results/csv/mit_election_lab/"
        response = requests.get(GITHUB_BASE + filepath)
        with open(os.path.join(self.cmd_path, BASE_PATH, filepath), "w") as f:
            f.write(response.text)

    def get_winning_vote(self, year, state_results):
        """
        Get winner in a race. Splits results by year.
        """
        race_results = [r for r in state_results if r["year"] == year]
        return max(race_results, key=lambda d: int(d["candidatevotes"]))

    def get_historical_votes(self, state_data, office):
        # Identify in each state Democrat and Republican candidates on the
        # ballot
        # Exclude writeins
        results = list(state_data)
        years = list(set([d["year"] for d in results]))
        winners_by_year = {}
        for year in years:
            winners_by_year[year] = self.get_winning_vote(year, results)

        democrats = []
        republicans = []
        others = []

        for row in results:
            candidate_votes = int(row["candidatevotes"])
            total_votes = int(row["totalvotes"])
            candidate_result = {
                "year": row["year"],
                "total": {
                    "votes": total_votes,
                    "votePct": 1 if total_votes > 0 else 0,
                },
            }
            # Allow for specials in Senate & House elections
            if office != "president":
                candidate_result["special"] = row["special"] == "TRUE"
            if (
                row["writein"] == "FALSE"
                and self.standard_party(row) == "republican"
            ):
                vote_pct = round(
                    candidate_votes / total_votes if total_votes > 0 else 0, 4
                )
                candidate_result["gop"] = {
                    "votes": candidate_votes,
                    "votePct": vote_pct,
                }
                if row == winners_by_year[row["year"]]:
                    candidate_result["winner"] = "gop"
                republicans.append(candidate_result)
            elif (
                row["writein"] == "FALSE"
                and self.standard_party(row) == "democrat"
            ):
                vote_pct = round(
                    candidate_votes / total_votes if total_votes > 0 else 0, 4
                )
                candidate_result["dem"] = {
                    "votes": candidate_votes,
                    "votePct": vote_pct,
                }
                if row == winners_by_year[row["year"]]:
                    candidate_result["winner"] = "dem"
                democrats.append(candidate_result)
            # If a write-in dem or republican or a third-party candidate is the
            # winner, we want to capture that, too.
            elif row == winners_by_year[row["year"]]:
                vote_pct = round(
                    candidate_votes / total_votes if total_votes > 0 else 0, 4
                )
                candidate_result["other"] = {
                    "votes": candidate_votes,
                    "votePct": vote_pct,
                }
                candidate_result["winner"] = "other"
                others.append(candidate_result)

        aggregated_result = defaultdict(dict)
        for d in republicans:
            aggregated_result[d["year"]].update(d)
        for d in democrats:
            aggregated_result[d["year"]].update(d)
        for d in others:
            aggregated_result[d["year"]].update(d)
        candidate_results_by_year = aggregated_result.values()

        return list(candidate_results_by_year)

    def get_state_race(self, division, division_var, body, cycle):
        ######
        # To get the Race, we provide:
        # 1. the division_level
        # 2. the division code
        # 3. the body (in case of the senate) or slug in the case of governor
        # 4. the cycle
        DIVISION = Division.objects.get(
            code=division_var, level__name=division
        )
        tqdm.write(self.TQDM_PREFIX + ">> {}        ".format(DIVISION))

        if body != "-governor":
            BODY = Body.objects.get(slug=body)
            Races = Race.objects.filter(
                cycle__slug=cycle, office__division=DIVISION, office__body=BODY
            )
        else:
            Races = Race.objects.filter(
                cycle__slug=cycle, office__slug=DIVISION.slug + body
            )

        return Races

    def format_state_data(self, body_data, key, division_level, body, office):
        tqdm.write(
            "Processing {} {} results for {}\n".format(
                division_level, office, body
            )
        )
        for k, v in tqdm(groupby(body_data, key=lambda x: x[key])):
            candidates = self.get_historical_votes(v, office)

            state_int = int(k)
            if state_int < 10:
                state_str = k.zfill(2)
            else:
                state_str = k

            # skip DC
            if state_str == "11":
                return

            # Get a state race's data for a specific body and cycle
            Races = self.get_state_race(
                division_level, state_str, body, "2018"
            )

            # Only pass data for active races
            if len(Races) == 0:
                continue

            for RACE in Races:
                # get an instance of a data profile for the race
                data_profile, created = DataProfile.objects.get_or_create(
                    race=RACE, defaults={"data": {}}
                )
                new_data = data_profile.data
                if office == "senate":
                    new_data["historicalResults"] = {
                        "president": data_profile.data.get(
                            "historicalResults", {}
                        ).get("president", None),
                        "seat": candidates,
                    }
                elif office == "president":
                    new_data["historicalResults"] = {
                        "president": candidates,
                        "seat": data_profile.data.get(
                            "historicalResults", {}
                        ).get("seat", None),
                    }

                data_profile, created = DataProfile.objects.update_or_create(
                    race=RACE, defaults={"data": new_data}
                )
        tqdm.write(self.TQDM_PREFIX + "✅  Done.                              ")

    def format_district_data(self, body_data, office):
        tqdm.write("Processing district results for {}\n".format(office))
        for k, v in tqdm(
            groupby(body_data, key=lambda x: (x["state_fips"], x["district"]))
        ):
            candidates = self.get_historical_votes(v, office)

            # let's split our key into separate fips components
            state_fips, district_fips = k

            state_int = int(state_fips)
            if state_int < 10:
                state_str = state_fips.zfill(2)
            else:
                state_str = state_fips

            # pad 0s
            district_int = int(district_fips)
            if district_int < 10:
                district_str = district_fips.zfill(2)
            else:
                district_str = district_fips

            try:
                DISTRICT = Division.objects.get(
                    code=district_str,
                    parent__code=state_str,
                    level__name=DivisionLevel.DISTRICT,
                )
            except ObjectDoesNotExist:
                continue
            tqdm.write(self.TQDM_PREFIX + ">> {}           ".format(DISTRICT))
            HOUSE = Body.objects.get(slug="house")
            Races = Race.objects.filter(
                cycle__slug="2018",
                office__division=DISTRICT,
                office__body=HOUSE,
                special=False,
            )

            # get an instance of a data profile for the race
            data_profile, created = DataProfile.objects.get_or_create(
                race=Races[0], defaults={"data": {}}
            )
            new_data = data_profile.data
            new_data["historicalResults"] = {
                "president": data_profile.data.get(
                    "historicalResults", {}
                ).get("president", None),
                "seat": candidates,
            }

            data_profile, created = DataProfile.objects.update_or_create(
                race=Races[0], defaults={"data": new_data}
            )
        tqdm.write(self.TQDM_PREFIX + "✅  Done.                             ")

    # Read in our historical data, sort and calculate votes + votePcts
    # Broken out by office. Senate/Governor == state_level results
    # House == district_level results
    def get_governor_data(self):
        self.download_csv("1976-2016-president.csv")
        president_data = self.read_csv("1976-2016-president.csv")
        president_data.sort(key=lambda x: x["state_fips"])
        self.format_state_data(
            president_data, "state_fips", "state", "-governor", "president"
        )

    def get_senate_data(self):
        self.download_csv("1976-2016-senate.csv")
        senate_data = self.read_csv("1976-2016-senate.csv")
        senate_data.sort(key=lambda x: x["state_fips"])
        self.format_state_data(
            senate_data, "state_fips", "state", "senate", "senate"
        )

        president_data = self.read_csv("1976-2016-president.csv")
        president_data.sort(key=lambda x: x["state_fips"])
        self.format_state_data(
            president_data, "state_fips", "state", "senate", "president"
        )

    def get_house_data(self):
        self.download_csv("1976-2016-house.csv")
        house_data = self.read_csv("1976-2016-house.csv")
        house_data.sort(key=lambda x: (x["state_fips"], x["district"]))
        self.format_district_data(house_data, "house")

    def handle(self, *args, **options):
        self.cmd_path = os.path.dirname(os.path.realpath(__file__))
        self.initialize_standardizer()
        self.get_governor_data()
        self.get_senate_data()
        self.get_house_data()

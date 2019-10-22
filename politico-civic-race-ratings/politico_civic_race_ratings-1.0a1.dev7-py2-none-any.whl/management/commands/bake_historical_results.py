# Imports from python.
import json
import os


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from race_ratings.
from raceratings.models import DataProfile
from raceratings.utils.aws import defaults
from raceratings.utils.aws import get_bucket


class Command(BaseCommand):
    help = "Publishes historical data"
    base_path = "election-results/2018/race-ratings/data/historical"

    def process_data(self, historical_results, body):
        if not historical_results:
            return None

        if body and body.slug == "senate":
            limit = self.senate_historical_limit
        else:
            limit = self.house_historical_limit

        for key, results_set in historical_results.items():
            if isinstance(results_set, list):
                if key == "seat":
                    results_set = [
                        r for r in results_set if r["special"] != "TRUE"
                    ]

                historical_results[key] = results_set[-limit:]

        return historical_results

    def bake_batch_house_file(self, profiles):
        key = os.path.join(self.base_path, "house.json")
        data = {}

        for profile in profiles:
            abbrev = "{}-{}".format(
                profile.race.office.division.parent.code_components["postal"],
                profile.race.office.division.code,
            )

            if profile.data.get("historicalResults"):
                seat_results = profile.data["historicalResults"]["seat"]
                seat_results = [
                    r for r in seat_results if r["special"] != "TRUE"
                ]
                seat_results = sorted(seat_results, key=lambda r: r["year"])

                pres_results = profile.data["historicalResults"]["president"]
                pres_results = sorted(pres_results, key=lambda r: r["year"])

                data[abbrev] = {}
                data[abbrev]["seat"] = seat_results[
                    -self.house_historical_limit :
                ]
                data[abbrev]["president"] = pres_results[
                    -self.house_historical_limit :
                ]
            else:
                data[abbrev] = None

        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(data),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_batch_senate_file(self, profiles):
        key = os.path.join(self.base_path, "senate.json")
        data = {}

        for profile in profiles:
            abbrev = "{}-{}".format(
                profile.race.office.division.code_components["postal"], "sen"
            )
            if profile.data.get("historicalResults"):
                seat_results = profile.data["historicalResults"]["seat"]
                seat_results = [
                    r for r in seat_results if r["special"] != "TRUE"
                ]
                seat_results = sorted(seat_results, key=lambda r: r["year"])

                pres_results = profile.data["historicalResults"]["president"]
                pres_results = sorted(pres_results, key=lambda r: r["year"])

                data[abbrev] = {}
                data[abbrev]["seat"] = seat_results[
                    -self.senate_historical_limit :
                ]
                data[abbrev]["president"] = pres_results[
                    -self.house_historical_limit :
                ]
            else:
                data[abbrev] = None

        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(data),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_data(self, profile):
        body = profile.race.office.body
        trimmed = self.process_data(
            profile.data.get("historicalResults"), body
        )

        if body and body.slug == "house":
            key = os.path.join(
                self.base_path,
                profile.race.office.division.parent.code,
                "house",
                profile.race.office.division.code,
                "data.json",
            )
        elif body and body.slug == "senate":
            key = os.path.join(
                self.base_path,
                profile.race.office.division.code,
                "senate",
                "data.json",
            )
        else:
            key = os.path.join(
                self.base_path,
                profile.race.office.division.code,
                "governor",
                "data.json",
            )

        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(trimmed),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "--s-historical-limit",
            dest="senate_historical_limit",
            action="store",
            default=6,
        )
        parser.add_argument(
            "--h-historical-limit",
            dest="house_historical_limit",
            action="store",
            default=3,
        )

    def handle(self, *args, **options):
        self.house_historical_limit = options["house_historical_limit"]
        self.senate_historical_limit = options["senate_historical_limit"]

        profiles = DataProfile.objects.exclude(race__office__body=None)

        house_profiles = DataProfile.objects.filter(
            race__office__body__slug="house"
        )
        senate_profiles = DataProfile.objects.filter(
            race__office__body__slug="senate", race__special=False
        )

        self.bake_batch_house_file(house_profiles)
        self.bake_batch_senate_file(senate_profiles)

        for profile in profiles:
            self.bake_data(profile)

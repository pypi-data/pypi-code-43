# Imports from python.
from itertools import chain
from itertools import groupby
import json


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
from rest_framework.renderers import JSONRenderer
from tqdm import tqdm


# Imports from race_ratings.
from raceratings.models import Category
from raceratings.serializers import BodyRatingSerializer
from raceratings.serializers import CategorySerializer
from raceratings.serializers import DistrictSerializer
from raceratings.serializers import RaceAPISerializer
from raceratings.serializers import RaceRatingFeedSerializer
from raceratings.serializers import StateSerializer
from raceratings.utils.aws import defaults
from raceratings.utils.aws import get_bucket
from raceratings.views import Home
from raceratings.views import RacePage


class Command(BaseCommand):
    help = "Publishes our race pages"

    def bake_home_page(self):
        view = Home()
        view.publish_statics()
        view.publish_serialized_data()
        view.publish_template()

    def bake_body_ratings(self):
        data = []
        bodies = Body.objects.all()

        for body in bodies:
            latest_rating = body.ratings.latest("created")
            data.append(BodyRatingSerializer(latest_rating).data)

        json_string = JSONRenderer().render(data)
        key = "election-results/2018/race-ratings/data/body-ratings.json"
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_api(self, races):
        data = RaceAPISerializer(races, many=True).data
        json_string = JSONRenderer().render(data)  # noqa
        key = "election-results/2018/race-ratings/data/ratings.json"
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_filters(self):
        categories = Category.objects.all()
        states = Division.objects.filter(level__name=DivisionLevel.STATE)
        districts = Division.objects.filter(level__name=DivisionLevel.DISTRICT)

        categories_data = CategorySerializer(categories, many=True).data
        states_data = StateSerializer(states, many=True).data
        districts_data = DistrictSerializer(districts, many=True).data

        data = {
            "categories": categories_data,
            "states": states_data,
            "districts": districts_data,
        }

        key = "election-results/2018/race-ratings/data/filters.json"
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(data),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_feed(self, races):
        ratings = [race.ratings.order_by("created")[1:] for race in races]
        ratings = list(chain(*ratings))
        ratings = sorted(ratings, key=lambda r: r.created)
        grouped = {}
        for key, group in groupby(ratings, lambda r: r.created):
            date = key.strftime("%Y-%m-%d")

            grouped[date] = [
                RaceRatingFeedSerializer(rating).data for rating in list(group)
            ]

        key = "election-results/2018/race-ratings/data/feed.json"
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(grouped),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def bake_rollup(self, races):
        house_races = races.filter(office__body__slug="house")
        senate_races = races.filter(office__body__slug="senate")
        governor_races = races.filter(office__body__isnull=True)

        data = {
            "house": self.rollup_chamber(house_races),
            "senate": self.rollup_chamber(senate_races),
            "governor": self.rollup_chamber(governor_races),
        }

        data["house"]["call"] = (
            Body.objects.get(slug="house")
            .ratings.latest("created")
            .category.short_label
        )
        data["senate"]["call"] = (
            Body.objects.get(slug="senate")
            .ratings.latest("created")
            .category.short_label
        )

        key = "election-results/2018/race-ratings/data/rollup.json"
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json.dumps(data),
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def rollup_chamber(self, races):
        ratings = [race.ratings.order_by("created").last() for race in races]
        ratings = sorted(ratings, key=lambda r: r.category.short_label)
        grouped = {}
        for key, group in groupby(ratings, lambda r: r.category.short_label):
            grouped[key] = len(list(group))

        return grouped

    def bake_race_pages(self, races):
        stub = RacePage()
        stub.publish_statics()

        for race in tqdm(races):
            if race.office.division.level.name == DivisionLevel.DISTRICT:
                division = race.office.division.parent.slug
                code = race.office.division.code
            else:
                division = race.office.division.slug
                code = None

            if race.special:
                code = "special"

            if "governor" in race.office.slug:
                body = "governor"
            else:
                body = race.office.body.slug

            self.stdout.write("> {}".format(race.office.label))
            kwargs = {"division": division, "body": body, "code": code}

            view = RacePage(**kwargs)
            view.publish_serialized_data()
            view.publish_template(**kwargs)

    def handle(self, *args, **kwargs):
        races = Race.objects.filter(
            cycle__slug="2018", special=False
        ).order_by("office__division__label")

        minnesota = Race.objects.filter(
            cycle__slug="2018",
            special=True,
            office__division__label="Minnesota",
            office__body__slug="senate",
        )

        mississippi = Race.objects.filter(
            cycle__slug="2018",
            special=True,
            office__division__label="Mississippi",
            office__body__slug="senate",
        )

        races = races | minnesota | mississippi

        self.bake_api(races)
        self.bake_feed(races)
        self.bake_filters()
        self.bake_body_ratings()
        self.bake_rollup(races)

        self.bake_home_page()

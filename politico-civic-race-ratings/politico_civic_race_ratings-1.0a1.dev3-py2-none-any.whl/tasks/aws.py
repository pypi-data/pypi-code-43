# Imports from python.
import json
import logging


# Imports from other dependencies.
from celery import shared_task
from election.models import Race
from government.models import Body
from itertools import chain, groupby
from rest_framework.renderers import JSONRenderer


# Imports from race_ratings.
from raceratings.serializers import BodyRatingSerializer
from raceratings.serializers import RaceAPISerializer
from raceratings.serializers import RaceRatingFeedSerializer
from raceratings.utils.aws import defaults
from raceratings.utils.aws import get_bucket


logger = logging.getLogger("tasks")

OUTPUT_PATH = "raceratings/data/"


@shared_task(acks_late=True)
def bake_api():
    races = Race.objects.filter(cycle__slug="2018", special=False).order_by(
        "office__division__label"
    )

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


@shared_task(acks_late=True)
def bake_body_ratings():
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


@shared_task(acks_late=True)
def bake_feed():
    races = Race.objects.filter(cycle__slug="2018", special=False).order_by(
        "office__division__label"
    )

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

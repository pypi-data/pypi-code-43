# Imports from Django.
from django.db.models.signals import post_save
from django.dispatch import receiver


# Imports from race_ratings.
from raceratings.celery import bake_api
from raceratings.celery import bake_body_ratings
from raceratings.celery import bake_feed
from raceratings.models import BodyRating
from raceratings.models import RaceRating


@receiver(post_save, sender=RaceRating)
def race_rating_save(sender, instance, **kwargs):
    pass
    # bake_api()
    # bake_feed()


@receiver(post_save, sender=BodyRating)
def body_rating_save(sender, instance, **kwargs):
    pass
    # bake_body_ratings()

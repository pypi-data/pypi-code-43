# Imports from Django.
from django.contrib.contenttypes.models import ContentType


# Imports from race_ratings.
from raceratings.models import RatingPageContent
from raceratings.models import RatingPageType


class Race(object):
    def bootstrap_race_content(self, race):
        RatingPageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(race),
            object_id=race.pk,
        )

        page_type, created = RatingPageType.objects.get_or_create(
            model_type="race"
        )

        RatingPageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
        )

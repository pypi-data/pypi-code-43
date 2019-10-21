# Imports from Django.
from django.contrib.contenttypes.models import ContentType


# Imports from race_ratings.
from raceratings.models import RatingPageContent
from raceratings.models import RatingPageType


class Home(object):
    def bootstrap_homepage_content(self):
        page_type, created = RatingPageType.objects.get_or_create(
            model_type="home"
        )

        RatingPageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
        )

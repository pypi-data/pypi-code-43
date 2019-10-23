# Imports from Django.
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PageContentManager(models.Manager):
    """
    Custom manager adds methods to serialize related content blocks.
    """

    @staticmethod
    def serialize_content_blocks(page_content):
        return {
            block.content_type.slug: block.content
            for block in page_content.blocks.all()
        }

    def race_content(self, race):
        """
        Return serialized content for an office page.
        """
        from raceratings.models import RatingPageType

        race_type = ContentType.objects.get_for_model(race)
        page_type = RatingPageType.objects.get(model_type="race")
        page_content = self.get(
            content_type__pk=race_type.pk, object_id=race.pk
        )
        page_type_content = self.get(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
        )
        return {
            "page": self.serialize_content_blocks(page_content),
            "page_type": self.serialize_content_blocks(page_type_content),
        }

    def home_content(self):
        from raceratings.models import RatingPageType

        page_type = RatingPageType.objects.get(model_type="home")
        page_content = self.get(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
        )

        return {"page": self.serialize_content_blocks(page_content)}

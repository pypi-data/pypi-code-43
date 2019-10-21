# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UUIDMixin


# Imports from race_ratings.
from raceratings.fields import MarkdownField


class RatingPageContentBlock(UUIDMixin, CivicBaseModel):
    """A block of content placed on an individual page."""

    natural_key_fields = ["id"]

    page = models.ForeignKey(
        "RatingPageContent", related_name="blocks", on_delete=models.PROTECT
    )
    content_type = models.ForeignKey(
        "RatingPageContentType", related_name="+", on_delete=models.PROTECT
    )
    content = MarkdownField()

    class Meta:
        unique_together = ("page", "content_type")

    def __str__(self):
        return self.content_type.name

# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from government.models import Body


# Imports from race_ratings.
from raceratings.fields import MarkdownField
from raceratings.models.author import Author
from raceratings.models.category import Category


class BodyRating(CivicBaseModel):
    """An individual rating for a governmental body."""

    natural_key_fields = ["body", "author", "created"]

    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="body_ratings"
    )
    body = models.ForeignKey(
        Body, on_delete=models.CASCADE, related_name="ratings"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="body_ratings"
    )
    explanation = MarkdownField(blank=True, null=True)

    class Meta:
        unique_together = ("body", "author", "created")

    def __str__(self):
        return "{0}: {1}".format(self.body.label, self.category.short_label)

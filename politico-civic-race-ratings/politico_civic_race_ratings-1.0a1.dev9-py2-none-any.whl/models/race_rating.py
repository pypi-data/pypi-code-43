# Imports from Django.
from django.contrib.postgres.fields import JSONField
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from election.models import Race


# Imports from race_ratings.
from raceratings.fields import MarkdownField
from raceratings.models.author import Author
from raceratings.models.category import Category


class RaceRating(CivicBaseModel):
    """An individual rating for a race."""

    natural_key_fields = ["race", "author", "created"]

    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="ratings"
    )
    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name="ratings"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="ratings"
    )
    explanation = MarkdownField(blank=True, null=True)

    class Meta:
        unique_together = ("race", "author", "created")

    def __str__(self):
        return "{0}: {1}".format(self.race.label, self.category.short_label)

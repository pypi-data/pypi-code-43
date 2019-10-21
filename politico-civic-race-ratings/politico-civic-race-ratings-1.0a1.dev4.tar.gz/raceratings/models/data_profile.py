# Imports from Django.
from django.contrib.postgres.fields import JSONField
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from election.models import Race


class DataProfile(CivicBaseModel):
    """Data about a specific race."""

    natural_key_fields = ["race"]

    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name="dataset"
    )
    data = JSONField()

    def __str__(self):
        return "{} profile".format(self.race.label)

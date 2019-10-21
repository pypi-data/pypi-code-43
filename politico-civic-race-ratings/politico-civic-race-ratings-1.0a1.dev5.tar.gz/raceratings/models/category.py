# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel


class Category(CivicBaseModel):
    """A category that races or bodies can be rated into."""

    natural_key_fields = ["label"]

    label = models.CharField(max_length=50, unique=True)
    short_label = models.CharField(max_length=30)
    order = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.label

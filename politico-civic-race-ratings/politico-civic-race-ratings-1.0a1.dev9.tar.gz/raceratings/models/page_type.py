# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UUIDMixin


class RatingPageType(UUIDMixin, CivicBaseModel):
    """A type of page that content can attach to."""

    natural_key_fields = ["model_type"]

    RACE = "Race"
    HOME = "Home"

    ALLOWED_TYPES = ((RACE, "race"), (HOME, "home"))

    model_type = models.CharField(
        max_length=4, choices=ALLOWED_TYPES, unique=True
    )

    def __str__(self):
        return self.get_model_type_display()

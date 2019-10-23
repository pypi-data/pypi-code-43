# Imports from Django.
from django.contrib.auth.models import User
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel


class Author(CivicBaseModel):
    """An author of race ratings."""

    natural_key_fields = ["first_name", "last_name"]

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rating_author",
    )

    class Meta:
        unique_together = ("first_name", "last_name")

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

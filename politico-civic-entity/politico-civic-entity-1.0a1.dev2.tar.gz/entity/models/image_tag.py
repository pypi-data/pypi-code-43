# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel


class ImageTag(CivicBaseModel):
    """
    Tags represent a type of image, which is used to serialize it.
    """

    default_serializer = "entity.serializers.ImageTagSerializer"
    natural_key_fields = ["name"]

    name = models.SlugField(unique=True)

    def __str__(self):
        return self.name

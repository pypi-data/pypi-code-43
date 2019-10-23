# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel


class OrganizationClassification(CivicBaseModel):
    default_serializer = (
        "entity.serializers.OrganizationClassificationSerializer"
    )
    natural_key_fields = ["name"]

    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name

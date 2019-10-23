# Imports from Django.
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from civic_utils.models import UUIDMixin


# Imports from entity.
from entity.fields import CountryField
from entity.models.organization_classification import (
    OrganizationClassification,
)


class Organization(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """An organization.

    Generally follows the Popolo spec:
    http://www.popoloproject.com/specs/organization.html
    """

    natural_key_fields = ["uid"]
    uid_prefix = "organization"
    uid_base_field = "name"
    default_serializer = "entity.serializers.OrganizationSerializer"

    name = models.CharField(max_length=500)

    identifiers = JSONField(null=True, blank=True)

    classification = models.ForeignKey(
        OrganizationClassification,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    national_headquarters = CountryField(default="US")

    founding_date = models.DateField(null=True, blank=True)
    dissolution_date = models.DateField(null=True, blank=True)

    summary = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="A one-line biographical summary.",
    )
    description = models.TextField(
        null=True, blank=True, help_text="A longer-form description."
    )

    links = ArrayField(
        models.URLField(),
        blank=True,
        null=True,
        help_text="External web links, comma-separated.",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        **uid**: :code:`person:{slug}`
        """
        self.generate_common_identifiers()

        super(Organization, self).save(*args, **kwargs)

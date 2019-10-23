# Imports from python.
import os
import uuid


# Imports from Django.
from django.db import models
from django.utils.html import format_html


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UUIDMixin


# Imports from entity.
from entity.models.image_tag import ImageTag
from entity.models.organization import Organization
from entity.utils.aws import StorageService


def person_image_path(instance, filename):
    return os.path.join(
        "cdn/images/organizations",
        instance.person.slug,
        "{}-{}{}".format(
            instance.tag, uuid.uuid4().hex[:6], os.path.splitext(filename)[1]
        ),
    )


class OrganizationImage(UUIDMixin, CivicBaseModel):
    """An image that has been linked to an organization and a tag type.

    Can be serialized by a tag.
    """

    natural_key_fields = ["organization", "tag"]
    default_serializer = "entity.serializers.OrganizationImageSerializer"

    # NOTE: Using UUIDMixin replaced the standard PK with a UUID.

    organization = models.ForeignKey(
        Organization, related_name="images", on_delete=models.PROTECT
    )
    tag = models.ForeignKey(
        ImageTag,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="Used to serialize images.",
    )
    image = models.ImageField(
        upload_to=person_image_path, storage=StorageService()
    )

    class Meta:
        unique_together = ("organization", "tag")

    def __str__(self):
        return "{} {}".format(self.organization.slug, self.tag.name)

    def preview(self):
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" style="max-height:100px; max-width: 300px;">'
            "</a>".format(self.image.url)
        )

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
from entity.models.person import Person


# Unfortunately, this is only around so the old migrations don't break
def person_image_path(instance, filename):
    return os.path.join(
        "cdn/images/people",
        instance.person.slug,
        "{}-{}{}".format(
            instance.tag, uuid.uuid4().hex[:6], os.path.splitext(filename)[1]
        ),
    )


class PersonImage(UUIDMixin, CivicBaseModel):
    """An image that has been linked to a person and a tag type.

    Can be serialized by a tag.
    """

    natural_key_fields = ["person", "tag"]
    default_serializer = "entity.serializers.PersonImageSerializer"

    # NOTE: Using UUIDMixin replaced the standard PK with a UUID.

    person = models.ForeignKey(
        Person, related_name="images", on_delete=models.PROTECT
    )
    tag = models.ForeignKey(
        ImageTag,
        related_name="+",
        on_delete=models.PROTECT,
        help_text="Used to serialize images.",
    )
    image = models.URLField()

    class Meta:
        unique_together = ("person", "tag")

    def __str__(self):
        return "{} {}".format(self.person.slug, self.tag.name)

    def preview(self):
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" style="max-height:100px; max-width: 300px;">'
            "</a>".format(self.image.url)
        )

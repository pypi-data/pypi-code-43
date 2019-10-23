# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin


class RatingPageContentType(CommonIdentifiersMixin, CivicBaseModel):
    """The kind of content contained in a content block.

    Used to serialize content blocks.
    """

    natural_key_fields = ["slug"]
    uid_prefix = "rating_page"
    uid_base_field = "name"

    slug = models.SlugField(
        blank=True,
        max_length=255,
        unique=True,
        editable=False,
        primary_key=True,
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.generate_common_identifiers(always_overwrite_slug=False)

        super(RatingPageContentType, self).save(*args, **kwargs)

    def get_uid_suffix(self):
        return self.slug

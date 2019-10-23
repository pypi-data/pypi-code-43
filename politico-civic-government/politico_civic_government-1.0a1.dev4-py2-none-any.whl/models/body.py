# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from civic_utils.models import UUIDMixin
from entity.models import Organization
from uuslug import slugify


# Imports from government.
from government.constants import STOPWORDS


class Body(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """
    A body represents a collection of offices or individuals organized around a
    common government or public service function.

    For example: the U.S. Senate, Florida House of Representatives, Columbia
    City Council, etc.

    .. note::
        Duplicate slugs are allowed on this model to accomodate states, for
        example:

        - florida/senate/
        - michigan/senate/
    """

    natural_key_fields = ["jurisdiction", "slug"]
    uid_prefix = "body"
    default_serializer = "government.serializers.BodySerializer"

    slug = models.SlugField(
        blank=True,
        max_length=255,
        editable=True,
        help_text="Customizable slug. Defaults to Org slug without stopwords.",
    )

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    organization = models.OneToOneField(
        Organization, related_name="government_body", on_delete=models.PROTECT
    )
    jurisdiction = models.ForeignKey("Jurisdiction", on_delete=models.PROTECT)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("jurisdiction", "slug")
        verbose_name_plural = "Bodies"

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`body:{slug}`
        **identifier**: :code:`<jurisdiction uid>__<this uid>`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=False, always_overwrite_uid=True
        )

        super(Body, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        return slugify(
            " ".join(
                w for w in self.organization.name.split() if w not in STOPWORDS
            )
        )

    def get_uid_prefix(self):
        return f"{self.jurisdiction.uid}__{self.uid_prefix}"

    def get_uid_suffix(self):
        return self.slug

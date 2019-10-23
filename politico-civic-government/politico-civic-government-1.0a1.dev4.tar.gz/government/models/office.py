# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from civic_utils.models import UUIDMixin
from geography.models import Division
from uuslug import slugify


# Imports from government.
from government.constants import STOPWORDS


class Office(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """
    An office represents a post, seat or position occuppied by an individual
    as a result of an election.

    For example: Senator, Governor, President, Representative.

    In the case of executive positions, like governor or president, the office
    is tied directlty to a jurisdiction. Otherwise, the office ties to a body
    tied to a jurisdiction.

    .. note::
        Duplicate slugs are allowed on this model to accomodate states, for
        example:

        - florida/house/seat-2/
        - michigan/house/seat-2/
    """

    uid_prefix = "office"
    default_serializer = "government.serializers.OfficeSerializer"

    FIRST_CLASS = "1"
    SECOND_CLASS = "2"
    THIRD_CLASS = "3"

    SENATE_CLASSES = (
        (FIRST_CLASS, "1st Class"),
        (SECOND_CLASS, "2nd Class"),
        (THIRD_CLASS, "3rd Class"),
    )

    slug = models.SlugField(blank=True, max_length=255, editable=True)

    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)
    senate_class = models.CharField(
        max_length=1, choices=SENATE_CLASSES, null=True, blank=True
    )

    division = models.ForeignKey(
        Division, related_name="offices", on_delete=models.PROTECT
    )
    jurisdiction = models.ForeignKey(
        "Jurisdiction",
        null=True,
        blank=True,
        related_name="offices",
        on_delete=models.PROTECT,
    )
    body = models.ForeignKey(
        "Body",
        null=True,
        blank=True,
        related_name="offices",
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = ("body", "jurisdiction", "slug")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`office:{slug}`
        **identifier**: :code:`<body uid/jurisdiction uid>__<this uid>`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=False, always_overwrite_uid=True
        )

        super(Office, self).save(*args, **kwargs)

    @classmethod
    def get_natural_key_definition(cls):
        return ["body", "jurisdiction", "slug"]

    def get_per_instance_natural_key_fields(self):
        if self.body:
            return [
                _ if not _.startswith("jurisdiction__") else None
                for _ in self.__class__.get_natural_key_fields()
            ]

        return [
            _ if not _.startswith("body__") else None
            for _ in self.get_natural_key_fields()
        ]

    def get_uid_base_field(self):
        return slugify(
            " ".join(w for w in self.name.split() if w not in STOPWORDS)
        )

    def get_uid_prefix(self):
        if self.body:
            return f"{self.body.uid}__{self.uid_prefix}"
        return f"{self.jurisdiction.uid}__{self.uid_prefix}"

    def get_uid_suffix(self):
        return self.slug

    @property
    def is_executive(self):
        """Is this an executive office?"""
        return self.body is None

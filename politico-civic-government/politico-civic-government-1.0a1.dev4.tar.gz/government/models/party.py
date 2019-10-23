# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from civic_utils.models import UUIDMixin
from entity.models import Organization
from uuslug import slugify


class Party(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """
    A political party.
    """

    natural_key_fields = ["slug"]
    uid_prefix = "party"
    default_serializer = "government.serializers.PartySerializer"

    slug = models.SlugField(
        blank=True,
        max_length=255,
        editable=True,
        unique=True,
        help_text="Customizable slug. Defaults to slugged Org name.",
    )

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    organization = models.OneToOneField(
        Organization,
        related_name="political_party",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="All parties except Independent should attach to an Org.",
    )

    ap_code = models.CharField(max_length=3, unique=True)
    aggregate_candidates = models.BooleanField(
        default=True,
        help_text=(
            "Determines whether to globally aggregate vote totals of this "
            "party's candidates during an election."
        ),
    )

    class Meta:
        verbose_name_plural = "Parties"

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field/identifier**: :code:`party:{slug}`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=False, always_overwrite_uid=True
        )

        super(Party, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        if self.organization:
            return slugify(self.organization.name)

        return slugify(self.label)

    def get_uid_suffix(self):
        return self.slug

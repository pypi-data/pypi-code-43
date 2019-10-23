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


class Jurisdiction(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """
    A Jurisdiction represents a logical unit of governance, comprised of
    a collection of legislative bodies, administrative offices or public
    services.

    For example: the United States Federal Government, the Government
    of the District of Columbia, Columbia Missouri City Government, etc.
    """

    natural_key_fields = ["division", "slug"]
    uid_prefix = "jurisdiction"
    default_serializer = "government.serializers.JurisdictionSerializer"

    name = models.CharField(max_length=255)

    division = models.ForeignKey(Division, null=True, on_delete=models.PROTECT)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`jurisdiction:{slug}`
        **identifier**: :code:`<division uid>__<this uid>`
        """
        self.generate_common_identifiers()

        super(Jurisdiction, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        return slugify(
            " ".join(w for w in self.name.split() if w not in STOPWORDS)
        )

    def get_uid_prefix(self):
        return f"{self.division.uid}__{self.uid_prefix}"

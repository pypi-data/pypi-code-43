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
from entity.fields import GenderField
from entity.fields import RaceField
from entity.fields import StateField


class Person(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """A real human being.🎵

    Generally follows the Popolo spec:
    http://www.popoloproject.com/specs/person.html
    """

    natural_key_fields = ["uid"]
    uid_prefix = "person"
    uid_base_field = "full_name"
    default_serializer = "entity.serializers.PersonSerializer"

    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    full_name = models.CharField(max_length=500, null=True, blank=True)

    identifiers = JSONField(null=True, blank=True)

    gender = GenderField(null=True, blank=True)
    race = RaceField(null=True, blank=True)
    nationality = CountryField(default="US")

    state_of_residence = StateField(
        null=True, blank=True, help_text="If U.S. resident."
    )

    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

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

    class Meta:
        verbose_name_plural = "People"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        """
        **uid**: :code:`person:{slug}`
        """
        if not self.full_name:
            self.full_name = "{0}{1}{2}".format(
                self.first_name,
                "{}".format(
                    " " + self.middle_name + " " if self.middle_name else " "
                ),
                self.last_name,
                "{}".format(" " + self.suffix if self.suffix else ""),
            )

        self.generate_common_identifiers()

        super(Person, self).save(*args, **kwargs)

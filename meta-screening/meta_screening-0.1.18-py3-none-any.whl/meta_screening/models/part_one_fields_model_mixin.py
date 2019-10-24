from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.db import models
from edc_constants.choices import PREG_YES_NO_NA, YES_NO, YES_NO_NA

from ..choices import ETHNICITY
from django_crypto_fields.fields.encrypted_char_field import EncryptedCharField


class PartOneFieldsModelMixin(models.Model):

    screening_consent = models.CharField(
        verbose_name=(
            "Has the subject given his/her verbal consent "
            "to be screened for the META trial?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    hospital_identifier = EncryptedCharField(unique=True)

    initials = EncryptedCharField(
        validators=[
            RegexValidator("[A-Z]{1,3}", "Invalid format"),
            MinLengthValidator(2),
            MaxLengthValidator(3),
        ],
        help_text="Use UPPERCASE letters only. May be 2 or 3 letters.",
    )

    ethnicity = models.CharField(
        max_length=15, choices=ETHNICITY, help_text="Used for eGFR calculation"
    )

    hiv_pos = models.CharField(
        verbose_name="Is the patient HIV positive", max_length=15, choices=YES_NO
    )

    art_six_months = models.CharField(
        verbose_name=(
            "Has the patient been on anti-retroviral therapy for at least 6 months"
        ),
        max_length=15,
        choices=YES_NO_NA,
    )

    on_rx_stable = models.CharField(
        verbose_name=("Is the patient considered to be stable on treatment "),
        max_length=15,
        choices=YES_NO_NA,
        help_text="in regular attendance for care",
    )

    lives_nearby = models.CharField(
        verbose_name=(
            "Is the patient living within the catchment population of the facility"
        ),
        max_length=15,
        choices=YES_NO,
    )

    staying_nearby = models.CharField(
        verbose_name=(
            "Is the patient planning to remain in the catchment area "
            "for at least 6 months"
        ),
        max_length=15,
        choices=YES_NO,
    )

    pregnant = models.CharField(
        verbose_name="Is the patient pregnant?", max_length=15, choices=PREG_YES_NO_NA
    )

    class Meta:
        abstract = True

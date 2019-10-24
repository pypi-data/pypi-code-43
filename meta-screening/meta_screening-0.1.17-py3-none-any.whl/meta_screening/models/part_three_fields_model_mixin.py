from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from edc_constants.choices import YES_NO, YES
from edc_model.models import BloodPressureModelMixin
from edc_model.validators import hm_validator

from ..choices import OGTT_UNITS, SERUM_CREATININE_UNITS
from edc_reportable.units import MILLIMOLES_PER_LITER


class PartThreeFieldsModelMixin(BloodPressureModelMixin, models.Model):

    part_three_report_datetime = models.DateTimeField(
        verbose_name="Second stage report date and time",
        null=True,
        blank=False,
        help_text="Date and time of report.",
    )

    weight = models.DecimalField(
        null=True,
        blank=False,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(15), MaxValueValidator(135)],
        help_text="in kgs",
    )

    height = models.DecimalField(
        null=True,
        blank=False,
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(100.0), MaxValueValidator(230.0)],
        help_text="in centimeters",
    )

    waist_circumference = models.DecimalField(
        verbose_name="Waist circumference",
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(50.0), MaxValueValidator(175.0)],
        null=True,
        blank=False,
        help_text="in centimeters",
    )

    fasted = models.CharField(
        verbose_name="Has the participant fasted?",
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    fasted_duration_str = models.CharField(
        verbose_name="How long have they fasted in hours and/or minutes?",
        max_length=8,
        validators=[hm_validator],
        null=True,
        blank=True,
        help_text="Duration of fast. Format is `HHhMMm`. For example 1h23m, 12h7m, etc",
    )

    fasted_duration_minutes = models.IntegerField(
        null=True, help_text="system calculated value"
    )

    hba1c_performed = models.CharField(
        verbose_name="Was the HbA1c performed?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        help_text="",
    )

    hba1c = models.DecimalField(
        verbose_name="HbA1c",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="in %",
    )

    creatinine_performed = models.CharField(
        verbose_name="Was the serum creatinine performed?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        help_text="",
    )

    creatinine = models.DecimalField(
        verbose_name="Serum creatinine levels",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    creatinine_units = models.CharField(
        verbose_name="Units (creatinine)",
        max_length=15,
        choices=SERUM_CREATININE_UNITS,
        null=True,
        blank=True,
    )

    # IFG
    fasting_glucose = models.DecimalField(
        verbose_name="Fasting glucose levels",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        null=True,
        blank=True,
        help_text="in mmol/L",
    )

    fasting_glucose_datetime = models.DateTimeField(
        verbose_name="Time fasting glucose level measured", null=True, blank=True
    )

    ogtt_base_datetime = models.DateTimeField(
        verbose_name="Time oral glucose solution was given",
        null=True,
        blank=True,
        help_text="(glucose solution given)",
    )

    ogtt_two_hr = models.DecimalField(
        verbose_name="Blood glucose level 2-hours after glucose solution given",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        null=True,
        blank=True,
        help_text="in mmol/L",
    )

    ogtt_two_hr_units = models.CharField(
        verbose_name="Units (Blood glucose)",
        max_length=15,
        choices=OGTT_UNITS,
        blank=True,
        editable=False,
        default=MILLIMOLES_PER_LITER,
    )

    ogtt_two_hr_datetime = models.DateTimeField(
        verbose_name="Time blood glucose levels 2-hours measured", null=True, blank=True
    )

    class Meta:
        abstract = True

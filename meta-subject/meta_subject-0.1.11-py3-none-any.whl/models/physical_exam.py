from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from edc_constants.choices import YES_NO
from edc_model.models import BaseUuidModel

from .crf_model_mixin import CrfModelMixin
from .model_mixins import VitalsFieldMixin


class PhysicalExam(VitalsFieldMixin, CrfModelMixin, BaseUuidModel):

    is_heartbeat_regular = models.CharField(
        verbose_name="Is the heart beat regular?", max_length=15, choices=YES_NO
    )

    irregular_heartbeat = models.TextField(
        "If the heartbeat is NOT regular, please describe", null=True, blank=True
    )

    waist_circumference = models.DecimalField(
        verbose_name="Waist circumference",
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(50.0), MaxValueValidator(175.0)],
        help_text="in centimeters",
    )

    jaundice = models.CharField(verbose_name="Jaundice", max_length=15, choices=YES_NO)

    peripheral_oedema = models.CharField(
        verbose_name="Presence of peripheral oedema", max_length=15, choices=YES_NO
    )

    has_abdominal_tenderness = models.CharField(
        verbose_name="Abdominal tenderness on palpation", max_length=15, choices=YES_NO
    )

    abdominal_tenderness = models.TextField(
        verbose_name="If YES, abdominal tenderness, please describe",
        null=True,
        blank=True,
    )

    has_enlarged_liver = models.CharField(
        verbose_name="Enlarged liver on palpation", max_length=15, choices=YES_NO
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Physical Exam"
        verbose_name_plural = "Physical Exams"

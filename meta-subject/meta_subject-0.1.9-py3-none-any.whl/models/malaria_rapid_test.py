from django.db import models
from edc_constants.choices import YES_NO, PRESENT_ABSENT_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model.models import BaseUuidModel

from .crf_model_mixin import CrfModelMixin


class MalariaRapidTest(CrfModelMixin, BaseUuidModel):

    performed = models.CharField(
        verbose_name="Was the malaria rapid test performed?",
        max_length=15,
        choices=YES_NO,
    )

    not_performed_reason = models.CharField(
        verbose_name="If NO, provide reason", max_length=150, null=True, blank=True
    )

    result = models.CharField(
        verbose_name="Result",
        max_length=25,
        choices=PRESENT_ABSENT_NA,
        default=NOT_APPLICABLE,
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Malaria Rapid Test"

from django.db import models
from edc_model.models import BaseUuidModel

from ..choices import WEIGHT_DETERMINATION
from .crf_model_mixin import CrfModelMixin
from .model_mixins import VitalsFieldMixin


class FollowupVitals(VitalsFieldMixin, CrfModelMixin, BaseUuidModel):

    weight_determination = models.CharField(
        verbose_name="Is weight estimated or measured?",
        max_length=15,
        choices=WEIGHT_DETERMINATION,
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Clinic follow up: Vitals"
        verbose_name_plural = "Clinic follow ups: Vitals"

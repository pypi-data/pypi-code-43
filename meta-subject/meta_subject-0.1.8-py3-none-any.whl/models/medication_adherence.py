from django.db import models
from edc_model.models import BaseUuidModel

from ..choices import MISSED_PILLS
from .crf_model_mixin import CrfModelMixin


class MedicationAdherence(CrfModelMixin, BaseUuidModel):

    visual_score = models.IntegerField(verbose_name="Visual score", help_text="%")

    last_missed_pill = models.CharField(
        verbose_name="When was the last time you missed your study pill?",
        max_length=25,
        choices=MISSED_PILLS,
    )

    pill_count = models.IntegerField(verbose_name="Number of pills left in the bottle")

    # Interviewer to read: People may miss taking their medicines for
    # various reasons. What was the reason you missed taking your
    # pills the last time?

    missed_pill_reason = models.TextField(
        verbose_name="Reasons for missing study pills", null=True, blank=True
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Medication Adherence"
        verbose_name_plural = "Medication Adherence"

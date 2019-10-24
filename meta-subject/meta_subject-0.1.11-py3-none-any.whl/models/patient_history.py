from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from meta_lists.models import Symptoms, ArvRegimens, OiProphylaxis, DiabetesSymptoms
from edc_reportable.units import (
    CELLS_PER_MILLIMETER_CUBED_DISPLAY,
    COPIES_PER_MILLILITER,
)
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model.models import BaseUuidModel
from edc_model_fields.fields import OtherCharField

from .crf_model_mixin import CrfModelMixin


class PatientHistory(CrfModelMixin, BaseUuidModel):

    symptoms = models.ManyToManyField(
        Symptoms, verbose_name="Do you have any of the following symptoms?"
    )

    other_symptoms = OtherCharField(null=True, blank=True)

    hiv_diagnosis_date = models.DateField(
        verbose_name="When was the diagnosis of HIV made?", null=True, blank=True
    )

    arv_initiation_date = models.DateField(
        verbose_name="Date of start of antiretroviral therapy (ART)",
        null=True,
        blank=True,
    )

    viral_load = models.IntegerField(
        verbose_name="Last viral load",
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
        null=True,
        blank=True,
        help_text=COPIES_PER_MILLILITER,
    )

    viral_load_date = models.DateField(
        verbose_name="Date of last viral load", null=True, blank=True
    )

    cd4 = models.IntegerField(
        verbose_name="Last CD4",
        validators=[MinValueValidator(0), MaxValueValidator(3000)],
        null=True,
        blank=True,
        help_text=CELLS_PER_MILLIMETER_CUBED_DISPLAY,
    )

    cd4_date = models.DateField(verbose_name="Date of last CD4", null=True, blank=True)

    current_arv_regimen = models.ForeignKey(
        ArvRegimens,
        on_delete=models.PROTECT,
        related_name="current_arv_regimen",
        verbose_name=(
            "Which antiretroviral therapy regimen is the patient currently on?"
        ),
        null=True,
        blank=False,
    )

    other_current_arv_regimen = OtherCharField(null=True, blank=True)

    current_arv_regimen_start_date = models.DateField(
        verbose_name=(
            "When did the patient start this current antiretroviral therapy regimen?"
        ),
        null=True,
        blank=True,
    )

    has_previous_arv_regimen = models.CharField(
        verbose_name="Has the patient been on any previous regimen?",
        max_length=15,
        choices=YES_NO,
    )

    previous_arv_regimen = models.ForeignKey(
        ArvRegimens,
        on_delete=models.PROTECT,
        related_name="previous_arv_regimen",
        verbose_name=(
            "Which antiretroviral therapy regimen was the patient previously on?"
        ),
        blank=True,
    )

    other_previous_arv_regimen = OtherCharField(null=True, blank=True)

    on_oi_prophylaxis = models.CharField(
        verbose_name=(
            "Is the patient on any prophylaxis against opportunistic infections?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    oi_prophylaxis = models.ManyToManyField(
        OiProphylaxis,
        verbose_name="If YES, which prophylaxis is the patient on?",
        blank=True,
    )

    other_oi_prophylaxis = OtherCharField(null=True, blank=True)

    hypertension = models.CharField(
        verbose_name="Has the patient been diagnosed with hypertension?",
        max_length=15,
        choices=YES_NO,
    )

    on_hypertension_treatment = models.CharField(
        verbose_name="Is the patient on treatment for hypertension?",
        max_length=15,
        choices=YES_NO,
    )

    hypertension_treatment = models.TextField(
        "What medications is the patient currently taking for hypertension?",
        null=True,
        blank=True,
    )

    statins = models.CharField(
        verbose_name="Is the patient currently taking any statins?",
        max_length=15,
        choices=YES_NO,
    )

    current_smoker = models.CharField(
        verbose_name="Is the patient a current smoker?", max_length=15, choices=YES_NO
    )

    former_smoker = models.CharField(
        verbose_name="Is the patient a previous smoker?",
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    diabetes_symptoms = models.ManyToManyField(
        DiabetesSymptoms,
        verbose_name="In the past year, have you had any of the following symptoms?",
    )

    other_past_year_symptoms = OtherCharField(null=True, blank=True)

    family_diabetics = models.CharField(
        verbose_name=(
            "Has anyone in your immediate family (parents, siblings, children) "
            "ever been diagnosed with diabetes?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Patient History"
        verbose_name_plural = "Patient History"

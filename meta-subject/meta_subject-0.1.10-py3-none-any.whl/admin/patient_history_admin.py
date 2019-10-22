from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_subject_admin
from ..forms import PatientHistoryForm
from ..models import PatientHistory
from .modeladmin import CrfModelAdmin


@admin.register(PatientHistory, site=meta_subject_admin)
class PatientHistoryAdmin(CrfModelAdmin):

    form = PatientHistoryForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Participant History",
            {
                "fields": (
                    "symptoms",
                    "other_symptoms",
                    "hiv_diagnosis_date",
                    "arv_initiation_date",
                    "viral_load",
                    "viral_load_date",
                    "cd4",
                    "cd4_date",
                    "current_arv_regimen",
                    "other_current_arv_regimen",
                    "current_arv_regimen_start_date",
                    "has_previous_arv_regimen",
                    "previous_arv_regimen",
                    "other_previous_arv_regimen",
                    "on_oi_prophylaxis",
                    "oi_prophylaxis",
                    "other_oi_prophylaxis",
                    "hypertension",
                    "on_hypertension_treatment",
                    "hypertension_treatment",
                    "statins",
                    "current_smoker",
                    "former_smoker",
                    "diabetes_symptoms",
                    "family_diabetics",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "has_previous_arv_regimen": admin.VERTICAL,
        "on_oi_prophylaxis": admin.VERTICAL,
        "hypertension": admin.VERTICAL,
        "on_hypertension_treatment": admin.VERTICAL,
        "statins": admin.VERTICAL,
        "current_smoker": admin.VERTICAL,
        "former_smoker": admin.VERTICAL,
        "family_diabetics": admin.VERTICAL,
        "current_arv_regimen": admin.VERTICAL,
        "previous_arv_regimen": admin.VERTICAL,
    }

    filter_horizontal = ("symptoms", "oi_prophylaxis", "diabetes_symptoms")

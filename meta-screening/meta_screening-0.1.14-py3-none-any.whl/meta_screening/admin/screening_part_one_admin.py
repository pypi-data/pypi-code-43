from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_screening_admin
from ..forms import ScreeningPartOneForm
from ..models import ScreeningPartOne
from .fieldsets import (
    get_part_one_fieldset,
    get_part_two_fieldset,
    get_part_three_fieldset,
)
from .subject_screening_admin import SubjectScreeningAdmin


@admin.register(ScreeningPartOne, site=meta_screening_admin)
class ScreeningPartOneAdmin(SubjectScreeningAdmin):

    form = ScreeningPartOneForm

    fieldsets = (
        get_part_one_fieldset(),
        get_part_two_fieldset(collapse=True),
        get_part_three_fieldset(collapse=True),
        audit_fieldset_tuple,
    )

    readonly_fields = (
        "part_two_report_datetime",
        "urine_bhcg_performed",
        "urine_bhcg",
        "urine_bhcg_date",
        "congestive_heart_failure",
        "liver_disease",
        "alcoholism",
        "acute_metabolic_acidosis",
        "renal_function_condition",
        "tissue_hypoxia_condition",
        "acute_condition",
        "metformin_sensitivity",
        "advised_to_fast",
        "appt_datetime",
        # part three
        "part_three_report_datetime",
        "weight",
        "height",
        "sys_blood_pressure",
        "dia_blood_pressure",
        "fasted",
        "fasted_duration_str",
        "hba1c_performed",
        "hba1c",
        "creatinine_performed",
        "creatinine",
        "creatinine_units",
        "fasting_glucose",
        "fasting_glucose_datetime",
        "ogtt_base_datetime",
        "ogtt_two_hr",
        "ogtt_two_hr_units",
        "ogtt_two_hr_datetime",
        # special exclusion
        "unsuitable_for_study",
        "reasons_unsuitable",
        # calculated values
        "calculated_bmi",
        "calculated_egfr",
        "converted_creatinine",
        "converted_ogtt_two_hr",
        "inclusion_a",
        "inclusion_b",
        "inclusion_c",
        "inclusion_d",
    )

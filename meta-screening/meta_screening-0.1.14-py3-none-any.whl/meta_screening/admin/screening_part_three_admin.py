from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_screening_admin
from ..forms import ScreeningPartThreeForm
from ..models import ScreeningPartThree
from .fieldsets import (
    calculated_values_fieldset,
    get_part_one_fieldset,
    get_part_two_fieldset,
    get_part_three_fieldset,
    special_exclusion_fieldset,
)
from .subject_screening_admin import SubjectScreeningAdmin


@admin.register(ScreeningPartThree, site=meta_screening_admin)
class ScreeningPartThreeAdmin(SubjectScreeningAdmin):

    form = ScreeningPartThreeForm

    fieldsets = (
        get_part_one_fieldset(collapse=True),
        get_part_two_fieldset(collapse=True),
        get_part_three_fieldset(),
        special_exclusion_fieldset,
        calculated_values_fieldset,
        audit_fieldset_tuple,
    )

    readonly_fields = (
        # part one
        "screening_consent",
        "report_datetime",
        "hospital_identifier",
        "initials",
        "gender",
        "age_in_years",
        "ethnicity",
        "consent_ability",
        "hiv_pos",
        "art_six_months",
        "on_rx_stable",
        "lives_nearby",
        "staying_nearby",
        "pregnant",
        # part two
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

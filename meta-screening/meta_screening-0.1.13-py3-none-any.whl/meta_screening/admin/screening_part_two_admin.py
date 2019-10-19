from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_screening_admin
from ..forms import ScreeningPartTwoForm
from ..models import ScreeningPartTwo
from .fieldsets import (
    get_part_one_fieldset,
    get_part_two_fieldset,
    get_part_three_fieldset,
    special_exclusion_fieldset,
)
from .subject_screening_admin import SubjectScreeningAdmin


@admin.register(ScreeningPartTwo, site=meta_screening_admin)
class ScreeningPartTwoAdmin(SubjectScreeningAdmin):

    post_url_on_delete_name = "screening_dashboard_url"
    subject_listboard_url_name = "screening_listboard_url"

    form = ScreeningPartTwoForm

    fieldsets = (
        get_part_one_fieldset(collapse=True),
        get_part_two_fieldset(),
        get_part_three_fieldset(collapse=True),
        special_exclusion_fieldset,
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

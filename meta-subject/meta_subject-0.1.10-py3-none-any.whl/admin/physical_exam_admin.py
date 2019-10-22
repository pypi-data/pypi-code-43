from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_subject_admin
from ..forms import PhysicalExamForm
from ..models import PhysicalExam
from .modeladmin import CrfModelAdmin


@admin.register(PhysicalExam, site=meta_subject_admin)
class PhysicalExamAdmin(CrfModelAdmin):

    form = PhysicalExamForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Physical examination",
            {
                "fields": (
                    "sys_blood_pressure",
                    "dia_blood_pressure",
                    "heart_rate",
                    "is_heartbeat_regular",
                    "irregular_heartbeat",
                    "respiratory_rate",
                    "temperature",
                    "weight",
                    "waist_circumference",
                    "jaundice",
                    "peripheral_oedema",
                    "has_abdominal_tenderness",
                    "abdominal_tenderness",
                    "has_enlarged_liver",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "is_heartbeat_regular": admin.VERTICAL,
        "jaundice": admin.VERTICAL,
        "peripheral_oedema": admin.VERTICAL,
        "has_abdominal_tenderness": admin.VERTICAL,
        "has_enlarged_liver": admin.VERTICAL,
    }

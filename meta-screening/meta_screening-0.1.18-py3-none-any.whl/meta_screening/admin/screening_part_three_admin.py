from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import meta_screening_admin
from ..forms import (
    ScreeningPartThreeForm,
    part_one_fields,
    part_two_fields,
    calculated_fields,
)
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

    readonly_fields = (*part_one_fields, *part_two_fields, *calculated_fields)

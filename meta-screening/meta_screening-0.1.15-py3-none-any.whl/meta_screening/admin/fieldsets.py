from django.utils.safestring import mark_safe

from ..forms import part_one_fields, part_two_fields, part_three_fields


def get_part_one_fieldset(collapse=None):

    dct = {
        "description": "To be completed by the research nurse",
        "fields": part_one_fields,
    }
    if collapse:
        dct.update(classes=("collapse",))
    return ("Part 1", dct)


def get_part_two_fieldset(collapse=None):
    dct = {
        "description": "To be completed by the study clinician",
        "fields": part_two_fields,
    }
    if collapse:
        dct.update(classes=("collapse",))
    return ("Part 2", dct)


def get_part_three_fieldset(collapse=None):
    dct = {
        "description": "To be completed by the study clinician",
        "fields": part_three_fields,
    }
    if collapse:
        dct.update(classes=("collapse",))
    return ("Part 3: Biomedical Indicators at Second Screening", dct)


special_exclusion_fieldset = (
    "Special Exclusion",
    {
        "description": mark_safe(
            "To be completed by the study clinician, if necessary."
            "<BR>A positive response, (e.g. YES), in this section <B>only</B> "
            "applies to criteria that is outside of the protocol "
            "inclusion and exclusion criteria above. "
        ),
        "fields": ("unsuitable_for_study", "reasons_unsuitable"),
    },
)

calculated_values_fieldset = (
    "Calculated values",
    {
        "classes": ("collapse",),
        "fields": (
            "calculated_bmi",
            "calculated_egfr",
            "converted_creatinine",
            "converted_ogtt_two_hr",
            "inclusion_a",
            "inclusion_b",
            "inclusion_c",
            "inclusion_d",
        ),
    },
)

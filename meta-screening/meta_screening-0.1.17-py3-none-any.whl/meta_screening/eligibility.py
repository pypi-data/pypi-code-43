from django.utils.safestring import mark_safe
from edc_constants.constants import FEMALE, MALE, YES, TBD, NO
from edc_utils.date import get_utcnow

from .calculators import (
    creatinine_to_umols_per_liter,
    converted_ogtt_two_hr,
    calculate_bmi,
    calculate_egfr,
)


class SubjectScreeningEligibilityError(Exception):
    pass


class EligibilityPartOneError(Exception):
    pass


class EligibilityPartTwoError(Exception):
    pass


class EligibilityPartThreeError(Exception):
    pass


part2_fields = [
    "congestive_heart_failure",
    "liver_disease",
    "alcoholism",
    "acute_metabolic_acidosis",
    "renal_function_condition",
    "tissue_hypoxia_condition",
    "acute_condition",
    "metformin_sensitivity",
]


def check_eligible_final(obj):
    """Updates model instance fields `eligible` and `reasons_ineligible`.
    """
    reasons_ineligible = []

    if obj.unsuitable_for_study == YES:
        obj.eligible = False
        reasons_ineligible.append("Subject unsuitable")
    else:
        obj.eligible = True if calculate_eligible_final(obj) == YES else False

    if obj.eligible:
        obj.reasons_ineligible = None
    else:
        if obj.reasons_ineligible_part_one:
            reasons_ineligible.append(obj.reasons_ineligible_part_one)
        if obj.reasons_ineligible_part_two:
            reasons_ineligible.append(obj.reasons_ineligible_part_two)
        if obj.reasons_ineligible_part_three:
            reasons_ineligible.append(obj.reasons_ineligible_part_three)
        if reasons_ineligible:
            obj.reasons_ineligible = "|".join(reasons_ineligible)
        else:
            obj.reasons_ineligible = None
    obj.eligibility_datetime = get_utcnow()


def calculate_eligible_final(obj):
    """Returns YES, NO or TBD.
    """
    eligible_final = NO
    valid_opts = [YES, NO, TBD]
    if any(
        [
            obj.eligible_part_one not in valid_opts,
            obj.eligible_part_two not in valid_opts,
            obj.eligible_part_three not in valid_opts,
        ]
    ):
        opts = [obj.eligible_part_one, obj.eligible_part_two, obj.eligible_part_three]
        raise SubjectScreeningEligibilityError(
            f"Invalid value for eligible. Got {opts}"
        )
    if any(
        [
            obj.eligible_part_one == TBD,
            obj.eligible_part_two == TBD,
            obj.eligible_part_three == TBD,
        ]
    ):
        eligible_final = TBD
    if all(
        [
            obj.eligible_part_one == YES,
            obj.eligible_part_two == YES,
            obj.eligible_part_three == YES,
        ]
    ):
        eligible_final = YES
    return eligible_final


def calculate_eligible_part_one(obj):
    """Updates model instance fields `eligible_part_one`
    and `reasons_ineligible_part_one`.
    """

    required_fields = [
        "consent_ability",
        "gender",
        "age_in_years",
        "hiv_pos",
        "art_six_months",
        "on_rx_stable",
        "lives_nearby",
        "staying_nearby",
        "pregnant",
    ]

    check_for_required_field_values(obj, required_fields, EligibilityPartOneError)

    reasons_ineligible = []
    if obj.consent_ability == NO:
        reasons_ineligible.append("Unable/unwilling to consent")
    if obj.gender not in [MALE, FEMALE]:
        reasons_ineligible.append("gender invalid")
    if obj.age_in_years < 18:
        reasons_ineligible.append("age<18")
    if obj.hiv_pos == NO:
        reasons_ineligible.append("not HIV+")
    if obj.art_six_months == NO:
        reasons_ineligible.append("ART<6m")
    if obj.on_rx_stable == NO:
        reasons_ineligible.append("ART not stable")
    if obj.lives_nearby == NO:
        reasons_ineligible.append("Not living nearby")
    if obj.staying_nearby == NO:
        reasons_ineligible.append("Unable/Unwilling to stay nearby")
    if obj.pregnant == YES:
        reasons_ineligible.append("Pregnant (unconfirmed)")
    eligible = NO if reasons_ineligible else YES
    obj.eligible_part_one = eligible
    obj.reasons_ineligible_part_one = "|".join(reasons_ineligible)


def calculate_eligible_part_two(obj):
    """Updates model instance fields `eligible_part_two`
    and `reasons_ineligible_part_two`.
    """

    check_for_required_field_values(obj, part2_fields, EligibilityPartTwoError)

    reasons_ineligible = []

    responses = {}
    for field in part2_fields:
        responses.update({field: getattr(obj, field)})
    for k, v in responses.items():
        if v == YES:
            reasons_ineligible.append(k.title().replace("_", " "))
    if not reasons_ineligible and obj.advised_to_fast == NO:
        reasons_ineligible.append("Not advised to fast")
    if not reasons_ineligible and not obj.appt_datetime:
        reasons_ineligible.append("Not scheduled for stage 2")
    eligible = NO if reasons_ineligible else YES
    obj.eligible_part_two = eligible
    obj.reasons_ineligible_part_two = "|".join(reasons_ineligible)


def calculate_eligible_part_three(obj):
    """Updates model instance fields `eligible_part_three`
    and `reasons_ineligible_part_three`.
    """
    required_fields = [
        "calculated_bmi",
        # "calculated_egfr",
        "fasting_glucose",
        "inclusion_a",
        "inclusion_b",
        "inclusion_c",
        "inclusion_d",
        "ogtt_two_hr",
    ]

    obj.converted_creatinine = creatinine_to_umols_per_liter(
        obj.creatinine, obj.creatinine_units
    )
    obj.converted_ogtt_two_hr = converted_ogtt_two_hr(obj)
    obj.calculated_bmi = calculate_bmi(obj)
    check_for_required_field_values(obj, required_fields, EligibilityPartThreeError)

    reasons_ineligible = []

    # BMI>30 combined with impaired fasting glucose (6.1 to 6.9 mmol/L)
    if (
        obj.calculated_bmi > 30.0
        and obj.fasting_glucose >= 6.1
        and obj.fasting_glucose <= 6.9
    ):
        obj.inclusion_a = YES
    else:
        obj.inclusion_a = NO

    # BMI>30 combined with impaired glucose tolerance at
    # 2 hours (7.0 to 11.10 mmol/L)
    if (
        obj.calculated_bmi > 30.0
        and obj.converted_ogtt_two_hr >= 7.0
        and obj.converted_ogtt_two_hr <= 11.10
    ):
        obj.inclusion_b = YES
    else:
        obj.inclusion_b = NO

    # BMI<=30 combined with impaired fasting glucose (6.3 to 6.9 mmol/L)
    if (
        obj.calculated_bmi <= 30.0
        and obj.fasting_glucose >= 6.3
        and obj.fasting_glucose <= 6.9
    ):
        obj.inclusion_c = YES
    else:
        obj.inclusion_c = NO

    # BMI<=30 combined with impaired glucose tolerance at 2 hours
    # (9.0 to 11.10 mmol/L)
    if (
        obj.calculated_bmi <= 30.0
        and obj.converted_ogtt_two_hr >= 9.0
        and obj.converted_ogtt_two_hr <= 11.10
    ):
        obj.inclusion_d = YES
    else:
        obj.inclusion_d = NO

    if any(
        [
            obj.inclusion_a == TBD,
            obj.inclusion_b == TBD,
            obj.inclusion_c == TBD,
            obj.inclusion_d == TBD,
        ]
    ):
        reasons_ineligible.append("BMI/IFT/OGTT incomplete")
    #         raise SubjectScreeningEligibilityError(
    #             "Part 3 inclusion criteria incomplete")
    if all(
        [
            obj.inclusion_a == NO,
            obj.inclusion_b == NO,
            obj.inclusion_c == NO,
            obj.inclusion_d == NO,
        ]
    ):
        reasons_ineligible.append("BMI/IFT/OGTT")
    obj.calculated_egfr = calculate_egfr(obj)
    if not obj.calculated_egfr:
        reasons_ineligible.append("eGFR not calculated")
    elif obj.calculated_egfr < 45.0:
        reasons_ineligible.append("eGFR<45")
    eligible = NO if reasons_ineligible else YES
    obj.eligible_part_three = eligible
    obj.reasons_ineligible_part_three = "|".join(reasons_ineligible)


def format_reasons_ineligible(*str_values):
    reasons = None
    str_values = [x for x in str_values if x is not None]
    if str_values:
        str_values = "".join(str_values)
        reasons = mark_safe(str_values.replace("|", "<BR>"))
    return reasons


def eligibility_status(obj):
    status_str = (
        f"P1: {obj.eligible_part_one.upper()}<BR>"
        f"P2: {obj.eligible_part_two.upper()}<BR>"
        f"P3: {obj.eligible_part_three.upper()}<BR>"
    )
    display_label = eligibility_display_label(obj)

    return status_str + display_label


def eligibility_display_label(obj):
    responses = [obj.eligible_part_one, obj.eligible_part_two, obj.eligible_part_three]
    if obj.eligible:
        display_label = '<font color="green"><B>ELIGIBLE</B></font>'
    elif TBD in responses and NO not in responses:
        display_label = '<font color="orange"><B>PENDING</B></font>'
    else:
        display_label = "<B>not eligible</B>"
    return display_label


def check_for_required_field_values(obj=None, required_fields=None, exception_cls=None):
    required_values = [getattr(obj, f) for f in required_fields]
    if not all(required_values):
        missing_values = {
            f: getattr(obj, f) for f in required_fields if not getattr(obj, f)
        }
        raise exception_cls(f"Missing required values. Got {missing_values}")

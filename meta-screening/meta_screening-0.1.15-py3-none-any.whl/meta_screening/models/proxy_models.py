from edc_constants.constants import TBD

from ..eligibility import (
    calculate_eligible_part_one,
    calculate_eligible_part_two,
    calculate_eligible_part_three,
    check_eligible_final,
    EligibilityPartOneError,
    EligibilityPartTwoError,
    EligibilityPartThreeError,
)
from .subject_screening import SubjectScreening


class ScreeningPartOne(SubjectScreening):
    def save(self, *args, **kwargs):
        try:
            calculate_eligible_part_one(self)
        except EligibilityPartOneError:
            self.eligible_part_one = TBD
            self.reasons_ineligible_part_one = ""
        else:
            check_eligible_final(self)
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Subject Screening: Part One"
        verbose_name_plural = "Subject Screening: Part One"


class ScreeningPartTwo(SubjectScreening):
    def save(self, *args, **kwargs):
        try:
            calculate_eligible_part_two(self)
        except EligibilityPartTwoError:
            check_eligible_final(self)
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Subject Screening: Part Two"
        verbose_name_plural = "Subject Screening: Part Two"


class ScreeningPartThree(SubjectScreening):
    def save(self, *args, **kwargs):
        try:
            calculate_eligible_part_three(self)
        except EligibilityPartThreeError:
            pass
        else:
            check_eligible_final(self)
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Subject Screening: Part Three"
        verbose_name_plural = "Subject Screening: Part Three"

from dateutil.relativedelta import relativedelta
from edc_constants.constants import FEMALE, MALE, BLACK, OTHER
from edc_reportable.units import (
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MICROMOLES_PER_LITER,
)
from edc_reportable.normal_reference import NormalReference
from edc_reportable.value_reference_group import ValueReferenceGroup
from edc_utils.date import get_utcnow


scr_reportable = ValueReferenceGroup(name="scr")
ref = NormalReference(
    name="scr",
    lower=0.2,
    upper=30.0,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MILLIGRAMS_PER_DECILITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)
scr_reportable.add_normal(ref)
ref = NormalReference(
    name="scr",
    lower=40,
    upper=130,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MICROMOLES_PER_LITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)
scr_reportable.add_normal(ref)


class CalculatorError(Exception):
    pass


class CalculatorUnitsError(Exception):
    pass


class ImpossibleValueError(Exception):
    pass


def converted_ogtt_two_hr(obj):
    """Return ogtt_two_hr in mmol/L or None.
    """
    # TODO: verify OGTT unit conversion
    if obj.ogtt_two_hr:
        if obj.ogtt_two_hr_units == MILLIGRAMS_PER_DECILITER:
            return float(obj.ogtt_two_hr) / 18
        elif obj.ogtt_two_hr_units == MILLIMOLES_PER_LITER:
            return float(obj.ogtt_two_hr)
        else:
            raise CalculatorUnitsError(
                f"Invalid units for `ogtt_two_hr`. Expected one "
                f"of [{MILLIGRAMS_PER_DECILITER}, {MILLIMOLES_PER_LITER}]. "
                f"Got {obj.ogtt_two_hr_units}."
            )
    return None


def converted_creatinine(obj):
    """Return Serum creatinine in micro-mol/L or None.
    """
    # TODO: verify creatinine unit conversion
    if obj.creatinine:
        if obj.creatinine_units == MILLIGRAMS_PER_DECILITER:
            return float(obj.creatinine) * 88.42
        elif obj.creatinine_units == MICROMOLES_PER_LITER:
            return float(obj.creatinine)
        else:
            raise CalculatorUnitsError(
                f"Invalid units for `creatinine`. Got {obj.creatinine_units}."
            )
    return None


def calculate_bmi(obj):
    calculated_bmi = None
    if obj.height and obj.weight:
        calculated_bmi = BMI(height_cm=obj.height, weight_kg=obj.weight).value
    return calculated_bmi


def calculate_egfr(obj):
    calculated_egfr = None
    if obj.gender and obj.age_in_years and obj.ethnicity and obj.converted_creatinine:
        opts = dict(
            gender=obj.gender,
            age=obj.age_in_years,
            ethnicity=obj.ethnicity,
            scr=obj.converted_creatinine,
            scr_units=MICROMOLES_PER_LITER,
        )
        calculated_egfr = eGFR(**opts).value
    return calculated_egfr


class BMI:
    """Calculate BMI, assume adult.
    """

    def __init__(self, weight_kg=None, height_cm=None):
        self.lower, self.upper = 5.0, 60.0
        self.weight = float(weight_kg)
        self.height = float(height_cm) / 100.0
        self.bmi = self.weight / (self.height ** 2)

    @property
    def value(self):
        if not (self.lower <= self.bmi <= self.upper):
            raise CalculatorError(
                f"BMI value is absurd. Weight(kg), Height(cm). Got {self.bmi}."
            )
        return self.bmi


class eGFR:

    """Reference http://nephron.com/epi_equation

    Levey AS, Stevens LA, et al. A New Equation to Estimate Glomerular
    Filtration Rate. Ann Intern Med. 2009; 150:604-612.
    """

    def __init__(self, gender=None, age=None, ethnicity=None, scr=None, scr_units=None):

        scr_units = MILLIGRAMS_PER_DECILITER if not scr_units else scr_units
        if scr_units not in [MILLIGRAMS_PER_DECILITER, MICROMOLES_PER_LITER]:
            raise CalculatorUnitsError(
                f"Invalid serum creatine units. "
                f"Expected on of {MILLIGRAMS_PER_DECILITER}, {MICROMOLES_PER_LITER}"
            )
        self.scr_units = scr_units

        if not gender or gender not in [MALE, FEMALE]:
            raise CalculatorError(
                f"Invalid gender. Expected on of {MALE}, {FEMALE}")
        self.gender = gender

        if not (18 < (age or 0) < 120):
            raise CalculatorError(
                f"Invalid age. See {self.__class__.__name__}. Got {age}"
            )
        self.age = float(age)

        self.ethnicity = ethnicity or OTHER

        normal = scr_reportable.get_normal(
            value=scr,
            gender=self.gender,
            units=self.scr_units,
            dob=get_utcnow() - relativedelta(years=self.age),
        )

        if not normal:
            raise ImpossibleValueError(
                f"Creatinine is abnormal. Got {scr}{self.scr_units}."
            )

        self.scr = float(scr) / 88.42  # serum creatinine mg/L

    @property
    def value(self):
        return (
            141.000
            * (min(self.scr / self.kappa, 1.000) ** self.alpha)
            * (max(self.scr / self.kappa, 1.000) ** -1.209)
            * self.age_factor
            * self.gender_factor
            * self.ethnicity_factor
        )

    @property
    def alpha(self):
        return -0.329 if self.gender == FEMALE else -0.411

    @property
    def kappa(self):
        return 0.7 if self.gender == FEMALE else 0.9

    @property
    def ethnicity_factor(self):
        return 1.150 if self.ethnicity == BLACK else 1.000

    @property
    def gender_factor(self):
        return 1.018 if self.gender == FEMALE else 1.000

    @property
    def age_factor(self):
        return 0.993 ** self.age

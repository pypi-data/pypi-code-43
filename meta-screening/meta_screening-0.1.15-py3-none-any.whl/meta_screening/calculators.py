from edc_constants.constants import FEMALE, MALE, BLACK, OTHER
from edc_reportable.units import (
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MICROMOLES_PER_LITER,
)


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


def creatinine_to_umols_per_liter(value, units):
    """Return Serum creatinine in micro-mol/L or None.
    """
    converted = None
    if value:
        if units == MILLIGRAMS_PER_DECILITER:
            converted = float(value) * 88.42
        elif units == MICROMOLES_PER_LITER:
            converted = float(value)
        else:
            raise CalculatorUnitsError(f"Invalid units for `creatinine`. Got {units}.")
    return converted


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
            scr=obj.converted_creatinine,  # umols/L
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

    def __init__(self, gender=None, age=None, ethnicity=None, scr=None):
        """Expects creatinine in umols/L.
        """

        if not gender or gender not in [MALE, FEMALE]:
            raise CalculatorError(f"Invalid gender. Expected on of {MALE}, {FEMALE}")
        self.gender = gender

        if not (18 < (age or 0) < 120):
            raise CalculatorError(
                f"Invalid age. See {self.__class__.__name__}. Got {age}"
            )
        self.age = float(age)

        self.ethnicity = ethnicity or OTHER
        self.scr = float(scr / 88.42)

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

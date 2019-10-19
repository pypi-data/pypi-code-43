from edc_constants.constants import FEMALE, MALE
from edc_reportable import site_reportables, parse as p, adult_age_options
from edc_reportable import MILLIGRAMS_PER_DECILITER, MILLIMOLES_PER_LITER
from edc_reportable import MICROMOLES_PER_LITER, IU_LITER
from edc_reportable import GRAMS_PER_DECILITER, TEN_X_9_PER_LITER
from edc_reportable.grading_data.daids_july_2017 import hematology, chemistries, dummies
from edc_reportable.units import CELLS_PER_MILLIMETER_CUBED, PERCENT, GRAMS_PER_LITER


normal_data = {
    "albumin": [
        p(
            "3.6<=x<=5.2",
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "36<=x<=52",
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "alp": [p("10<=x<=40", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "alt": [p("10<=x<=40", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "amylase": [
        p("40<=x<=140", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)
    ],
    "ast": [p("10<=x<=40", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "egfr": [],
    "creatinine": [
        p(
            "0.6<=x<=1.3",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "53<=x<=115",
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "glucose": [
        p(
            "4.0<=x<=6.11",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            fasting=True,
            **adult_age_options,
        ),
        p(
            "4.0<=x<=6.44",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            fasting=False,
            **adult_age_options,
        ),
    ],
    "hba1c": [
        p("4.4<=x<=6.6", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)
    ],
    "ggt": [p("0<=x<=30", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "haemoglobin": [
        p(
            "13.5<=x<=17.5",
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        p(
            "12.0<=x<=15.5",
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
    ],
    # hematocrit
    "hct": [
        p("37.0<=x<=54.0", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)
    ],
    "magnesium": [
        p(
            "0.75<=x<=1.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.8<=x<=2.9",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "neutrophil": [
        p(
            "2.5<=x<=7.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "platelets": [
        p(
            "150<=x<=450",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "150000<=x<=450000",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "potassium": [
        p(
            "3.6<=x<=5.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "sodium": [
        p(
            "135<=x<=145",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    # BUN
    "urea": [
        p(
            "2.5<=x<=6.5",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "uric_acid": [
        p(
            "0.400<=x",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "7.2<=x",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "rbc": [
        p(
            "3.5<=x<=5.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3500<=x<=5500",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "wbc": [
        p("2.49<x", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **adult_age_options)
    ],
}

grading_data = {}
grading_data.update(**dummies)
grading_data.update(**chemistries)
grading_data.update(**hematology)

site_reportables.register(
    name="meta", normal_data=normal_data, grading_data=grading_data
)

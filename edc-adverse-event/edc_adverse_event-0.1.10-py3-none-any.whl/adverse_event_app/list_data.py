from edc_list_data import PreloadData
from edc_constants.constants import OTHER, NOT_APPLICABLE, DEAD, MALIGNANCY, UNKNOWN


list_data = {
    "edc_adverse_event.causeofdeath": [
        ("bacteraemia", "Bacteraemia"),
        ("bacterial_pneumonia", "Bacterial pneumonia"),
        (MALIGNANCY, "Malignancy"),
        ("art_toxicity", "ART toxicity"),
        ("IRIS_non_CM", "IRIS non-CM"),
        ("diarrhea_wasting", "Diarrhea/wasting"),
        (UNKNOWN, "Unknown"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.aeclassification": [
        ("anaemia", "Anaemia"),
        ("bacteraemia/sepsis", "Bacteraemia/Sepsis"),
        ("CM_IRIS", "CM IRIS"),
        ("diarrhoea", "Diarrhoea"),
        ("hypokalaemia", "Hypokalaemia"),
        ("neutropaenia", "Neutropaenia"),
        ("pneumonia", "Pneumonia"),
        ("renal_impairment", "Renal impairment"),
        ("respiratory_distress", "Respiratory distress"),
        ("TB", "TB"),
        ("thrombocytopenia", "Thrombocytopenia"),
        ("thrombophlebitis", "Thrombophlebitis"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.saereason": [
        (NOT_APPLICABLE, "Not applicable"),
        (DEAD, "Death"),
        ("life_threatening", "Life-threatening"),
        ("significant_disability", "Significant disability"),
        (
            "in-patient_hospitalization",
            (
                "In-patient hospitalization or prolongation "
                "(17 or more days from study inclusion)"
            ),
        ),
        (
            "medically_important_event",
            "Medically important event (e.g. Severe thrombophlebitis, Bacteraemia, "
            "recurrence of symptoms not requiring admission, Hospital acquired "
            "pneumonia)",
        ),
    ],
}

preload_data = PreloadData(
    list_data=list_data, model_data={}, unique_field_data=None)

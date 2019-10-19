from django.conf import settings
from edc_constants.constants import OTHER, UNKNOWN, DEAD, NONE
from edc_list_data import PreloadData
from meta_prn.constants import WITHDRAWAL, TRANSFERRED, LATE_EXCLUSION


list_data = {
    "meta_lists.diabetessymptoms": [
        ("frequent_urination", "Wanting to urinate more often than usual"),
        ("excessive_thirst", "Wanting to drink water more than usual"),
        ("excessive_eating", "Wanting to eat food more than usual"),
        (NONE, "No symptoms to report"),
    ],
    "meta_lists.oiprophylaxis": [
        ("tmp_smx", "TMP/SMX"),
        ("fluconazole", "Fluconazole"),
        ("isoniazid", "Isoniazid"),
        (OTHER, "Other, specify"),
    ],
    "meta_lists.symptoms": [
        ("nausea", "Nausea"),
        ("vomiting", "Vomiting"),
        ("abdominal_pain_general", "Abdominal pain (General)"),
        ("abdominal_pain_right_upper_quad", "Abdominal pain (Right upper quadrant)"),
        ("loss_of_appetite", "Loss of appetite"),
        ("flatulence", "Flatulence (gas)"),
        ("dizziness", "Dizziness"),
        ("shakiness", "Shakiness"),
        ("headaches", "Headaches"),
        ("sweating", "Sweating"),
        ("fatigue", "Fatigue"),
        ("weakness", "Weakness"),
        ("muscle_pain", "Muscle pain"),
        ("muscle_cramping", "Muscle cramping"),
        ("pounding_heartbeat", "Fast or pounding heartbeat"),
        ("shallow_breathing", "Fast or shallow breathing"),
        ("unusual_sleepiness", "Unusual sleepiness"),
        (NONE, "No symptoms to report"),
        (OTHER, "Other, specify"),
    ],
    "meta_lists.baselinesymptoms": [
        ("loss_of_weight", "Loss of weight"),
        ("skin_infection", "Skin infection"),
        ("sweating", "Sweating"),
        ("vomiting", "Vomiting"),
        ("headaches", "Headaches"),
        ("shakiness", "Shakiness"),
        ("dizziness", "Dizziness"),
        ("unusual_sleepiness", "Unusual sleepiness"),
        ("shallow_breathing", "Fast or shallow breathing"),
        ("muscle_cramping", "Muscle cramping"),
        ("weakness", "Weakness"),
        ("fatigue", "Fatigue"),
        ("cough", "Cough"),
        ("loss_of_appetite", "Loss of appetite"),
        ("diarrhoea", "Diarrhoea"),
        ("abdominal_pain_general", "Abdominal pain (General)"),
        (NONE, "No symptoms to report"),
        (OTHER, "Other, specify"),
    ],
    "meta_lists.arvregimens": [
        ("TDF_3TC_ATV_r", "TDF + 3TC + ATV/r"),
        ("TDF_FTC_ATV_r", "TDF + FTC + ATV/r"),
        ("TDF_3TC_LPV_r", "TDF + 3TC + LPV/r"),
        ("AZT_3TC_ATV_r", "AZT + 3TC + ATV/r"),
        ("AZT_3TC_LPV_r", "AZT + 3TC + LPV/r"),
        ("ABC_3TC_ATV_r", "ABC + 3TC + ATV/r"),
        ("ABC_3TC_LPV_r", "ABC + 3TC + LPV/r"),
        ("TDF_FTC_LPV_r", "TDF + FTC + LPV/r"),
        ("DTG_ABC/3TC_ATV_r", "DTG + (ABC/3TC) + ATV/r"),
        (UNKNOWN, "Unknown"),
        (OTHER, "Other, specify"),
    ],
    "meta_lists.offstudyreasons": [
        ("completed_followup", "Patient completed 12 months of follow-up"),
        ("clinical_endpoint", "Patient reached a clinical endpoint"),
        ("toxicity", "Patient experienced an unacceptable toxicity"),
        (
            "intercurrent_illness",
            "Intercurrent illness which prevents further treatment",
        ),
        ("lost_to_followup", "Patient lost to follow-up"),
        (DEAD, "Patient reported/known to have died"),
        (WITHDRAWAL, "Patient withdrew consent to participate further"),
        (LATE_EXCLUSION, "Patient fulfilled late exclusion criteria*"),
        (TRANSFERRED, "Patient has been transferred to another health centre"),
        (
            OTHER,
            (
                "Other condition that justifies the discontinuation of "
                "treatment in the clinician’s opinion (specify below)"
            ),
        ),
    ],
}


if settings.APP_NAME != "meta_lists":
    preload_data = PreloadData(list_data=list_data)

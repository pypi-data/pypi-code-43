from edc_permissions.utils import get_pii_models

extra_pii_models = [
    "meta_consent.subjectconsent",
    "meta_consent.subjectreconsent",
    "meta_screening.subjectscreening",
]

pii_models = get_pii_models(extra_pii_models)

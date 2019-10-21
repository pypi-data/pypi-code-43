from edc_permissions.codenames import pii_view

pii_view += [
    "meta_consent.view_historicalsubjectreconsent",
    "meta_consent.view_subjectreconsent",
    "meta_screening.view_historicalsubjectscreening",
    "meta_screening.view_subjectscreening",
]

pii_view.sort()

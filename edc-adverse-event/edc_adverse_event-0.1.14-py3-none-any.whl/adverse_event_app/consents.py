import arrow

from django.apps import apps as django_apps
from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents
from edc_constants.constants import MALE, FEMALE
from dateutil.relativedelta import relativedelta

edc_protocol = django_apps.get_app_config("edc_protocol")

v1 = Consent(
    "adverse_event_app.subjectconsent",
    version="1",
    start=arrow.utcnow().floor("hour") - relativedelta(years=1),
    end=arrow.utcnow().ceil("hour"),
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
)

site_consents.register(v1)

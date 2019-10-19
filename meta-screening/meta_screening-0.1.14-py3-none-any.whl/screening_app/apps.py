from django.apps import AppConfig as DjangoAppConfig
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig


class AppConfig(DjangoAppConfig):
    name = 'screening_app'


class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
    country = "tanzania"
    definitions = {
        "7-day-clinic": dict(
            days=[MO, TU, WE, TH, FR, SA, SU],
            slots=[100, 100, 100, 100, 100, 100, 100],
        ),
        "5-day-clinic": dict(
            days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
        ),
    }

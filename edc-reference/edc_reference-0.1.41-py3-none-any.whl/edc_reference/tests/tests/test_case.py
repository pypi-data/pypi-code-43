from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.test import TestCase as BaseTestCase
from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility import import_holidays
from edc_reference.reference_model_config import ReferenceModelConfig
from edc_reference.site_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from reference_app.consents import v1
from reference_app.models import SubjectVisit, SubjectConsent, OnSchedule
from reference_app.visit_schedules import visit_schedule


class TestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import_holidays()
        site_consents.registry = {}
        site_consents.register(v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        Site.objects.create(id=10, name="edc", domain="edc.example.com")

    def setUp(self):
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False

        ref_config = ReferenceModelConfig(
            name="reference_app.subjectvisit",
            fields=["report_datetime", "visit_code", "visit_code_sequence"],
        )
        site_reference_configs.register(ref_config)

        self.testmodel_reference = ReferenceModelConfig(
            name="reference_app.testmodel", fields=["field_str", "report_datetime"]
        )
        site_reference_configs.register(self.testmodel_reference)

        self.crfone_reference = ReferenceModelConfig(
            name="reference_app.crfone",
            fields=[
                "field_str",
                "field_date",
                "field_datetime",
                "field_int",
                "report_datetime",
            ],
        )
        site_reference_configs.register(self.crfone_reference)

        self.subject_identifier = "12345678"

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity="123456789",
            confirm_identity="123456789",
        )

        on_schedule = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(days=10),
        )
        on_schedule.put_on_schedule()
        appointment = Appointment.objects.get(timepoint=0.0)
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(days=10),
            reason=SCHEDULED,
            appointment=appointment,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code="1000",
            visit_code_sequence=0,
        )

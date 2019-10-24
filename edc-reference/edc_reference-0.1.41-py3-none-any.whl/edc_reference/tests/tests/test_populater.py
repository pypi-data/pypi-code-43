from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_reference.models import Reference
from edc_reference.populater import Populater
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from reference_app.models import SubjectVisit, CrfOne, SubjectConsent
from reference_app.visit_schedules import visit_schedule


class TestPopulater(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"

        dte = get_utcnow()

        SubjectConsent.objects.create(
            consent_datetime=dte - relativedelta(days=10),
            subject_identifier=self.subject_identifier,
            identity="012345678",
            confirm_identity="012345678",
        )

        appointment1 = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=dte - relativedelta(days=10),
            timepoint_datetime=dte - relativedelta(days=10),
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            visit_code="1000",
            timepoint=Decimal("1.0"),
        )

        appointment2 = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=dte,
            timepoint_datetime=dte,
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            visit_code="2000",
            timepoint=Decimal("2.0"),
        )

        self.subject_visit1 = SubjectVisit.objects.create(
            appointment=appointment1,
            report_datetime=appointment1.appt_datetime,
            reason=SCHEDULED,
        )

        CrfOne.objects.create(
            subject_visit=self.subject_visit1,
            field_date=self.subject_visit1.report_datetime.date(),
            field_datetime=self.subject_visit1.report_datetime,
            field_int=1,
            field_str="erik",
        )

        self.subject_visit2 = SubjectVisit.objects.create(
            appointment=appointment2,
            report_datetime=appointment2.appt_datetime,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(
            subject_visit=self.subject_visit2,
            field_date=self.subject_visit2.report_datetime.date(),
            field_datetime=self.subject_visit2.report_datetime,
            field_int=1,
            field_str="erik",
        )

    def test_populates_for_visit(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="reference_app.subjectvisit",
                        report_datetime=visit.report_datetime,
                        field_name="report_datetime",
                        value_datetime=visit.report_datetime,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_date(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="reference_app.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_date",
                        value_date=visit.report_datetime.date(),
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_datetime(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="reference_app.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_datetime",
                        value_datetime=visit.report_datetime,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_str(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        report_datetime=visit.report_datetime,
                        model="reference_app.crfone",
                        field_name="field_str",
                        value_str="erik",
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_int(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="reference_app.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_int",
                        value_int=1,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populater_updates(self):
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="reference_app.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_int",
                        value_int=1,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")
